import sys
import json
import subprocess
import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from kali_orchestrator.catalog import build_default_catalog
from kali_orchestrator.config import ConfigError, load_config
from kali_orchestrator.policy import AuthorizationError, ExecutionPolicy, TargetScope
from kali_orchestrator.runner import RunnerError, ToolRunner


class TargetScopeTests(unittest.TestCase):
    def test_allows_exact_domain_and_subdomains(self):
        scope = TargetScope.from_values(domains=["example.test"])

        self.assertTrue(scope.allows("https://example.test/login"))
        self.assertTrue(scope.allows("https://api.example.test/v1"))
        self.assertFalse(scope.allows("https://example.test.evil.test"))
        self.assertFalse(scope.allows("https://other.test"))

    def test_allows_ip_inside_authorized_cidr(self):
        scope = TargetScope.from_values(networks=["192.0.2.0/24"])

        self.assertTrue(scope.allows("192.0.2.10"))
        self.assertFalse(scope.allows("192.0.3.10"))


class ExecutionPolicyTests(unittest.TestCase):
    def test_rejects_out_of_scope_target(self):
        policy = ExecutionPolicy(scope=TargetScope.from_values(domains=["example.test"]))

        with self.assertRaises(AuthorizationError):
            policy.assert_can_run("safe-web", "https://other.test")

    def test_requires_explicit_authorization_for_active_profiles(self):
        policy = ExecutionPolicy(
            scope=TargetScope.from_values(domains=["example.test"]),
            authorized=False,
        )

        with self.assertRaises(AuthorizationError):
            policy.assert_can_run("active", "https://example.test")

        authorized = ExecutionPolicy(
            scope=TargetScope.from_values(domains=["example.test"]),
            authorized=True,
        )
        authorized.assert_can_run("active", "https://example.test")


class CatalogTests(unittest.TestCase):
    def test_initial_catalog_contains_requested_tools(self):
        catalog = build_default_catalog()
        expected = {"nmap", "nuclei", "owasp-zap", "burp-suite", "sqlmap", "gitleaks", "trufflehog", "trivy"}

        self.assertTrue(expected.issubset(catalog.names()))

    def test_unavailable_tool_is_reported_without_execution(self):
        catalog = build_default_catalog()
        tool = catalog.get("nmap")

        self.assertIn(tool.availability(), {"installed", "not-installed"})
        self.assertEqual(tool.status(), "available" if tool.is_installed() else "not-installed")


class ConfigAndCliTests(unittest.TestCase):
    def test_loads_and_validates_safe_plan(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            path.write_text(
                json.dumps(
                    {
                        "scope": {"domains": ["example.test"]},
                        "profile": "safe-web",
                        "targets": ["https://example.test"],
                        "tools": ["nmap", "nuclei"],
                    }
                )
            )

            config = load_config(path)

        self.assertEqual(config.profile, "safe-web")
        self.assertEqual(config.tools, ("nmap", "nuclei"))

    def test_rejects_active_plan_without_authorization(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            path.write_text(
                json.dumps(
                    {
                        "scope": {"domains": ["example.test"]},
                        "profile": "active",
                        "targets": ["example.test"],
                        "tools": ["sqlmap"],
                    }
                )
            )

            with self.assertRaises(ConfigError):
                load_config(path)

    def test_accepts_real_execution_plan_only_with_authorization(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            path.write_text(
                json.dumps(
                    {
                        "scope": {"domains": ["example.test"]},
                        "profile": "safe-web",
                        "authorized": True,
                        "dry_run": False,
                        "targets": ["example.test"],
                        "tools": ["nmap"],
                    }
                )
            )

            config = load_config(path)

        self.assertFalse(config.dry_run)
        self.assertTrue(config.authorized)

    def test_cli_plan_is_dry_and_reports_tool_status(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "audit.json"
            path.write_text(
                json.dumps(
                    {
                        "scope": {"domains": ["example.test"]},
                        "profile": "safe-web",
                        "targets": ["example.test"],
                        "tools": ["nmap"],
                    }
                )
            )
            result = subprocess.run(
                [sys.executable, "-m", "kali_orchestrator", "plan", "--config", str(path)],
                cwd=ROOT,
                env={**dict(), "PYTHONPATH": str(ROOT / "src")},
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads(result.stdout)
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["targets"], ["example.test"])
        self.assertEqual(plan["tools"][0]["name"], "nmap")


class RunnerTests(unittest.TestCase):
    def setUp(self):
        catalog = build_default_catalog()
        catalog.register(
            replace(
                catalog.get("nmap"),
                name="fake-tool",
                binary=sys.executable,
                profiles=("safe-web",),
            )
        )
        self.catalog = catalog
        self.scope = TargetScope.from_values(domains=["example.test"])

    def test_dry_run_never_executes_command(self):
        policy = ExecutionPolicy(scope=self.scope, authorized=False)
        result = ToolRunner(self.catalog).run(
            "fake-tool",
            profile="safe-web",
            target="example.test",
            args=["-c", "raise SystemExit(99)"],
            policy=policy,
            dry_run=True,
        )

        self.assertEqual(result.status, "planned")
        self.assertEqual(result.returncode, None)
        self.assertEqual(result.stdout, "")

    def test_execution_requires_authorization_and_redacts_output(self):
        with self.assertRaises(RunnerError):
            ToolRunner(self.catalog).run(
                "fake-tool",
                profile="safe-web",
                target="example.test",
                args=["-c", "print('Authorization: Bearer secret-token')"],
                policy=ExecutionPolicy(scope=self.scope, authorized=False),
                dry_run=False,
            )

        result = ToolRunner(self.catalog).run(
            "fake-tool",
            profile="safe-web",
            target="example.test",
            args=["-c", "print('Authorization: Bearer secret-token')"],
            policy=ExecutionPolicy(scope=self.scope, authorized=True),
            dry_run=False,
        )

        self.assertEqual(result.status, "completed")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[REDACTED]", result.stdout)
        self.assertNotIn("secret-token", result.stdout)

    def test_timeout_is_reported(self):
        result = ToolRunner(self.catalog).run(
            "fake-tool",
            profile="safe-web",
            target="example.test",
            args=["-c", "import time; time.sleep(1)"],
            policy=ExecutionPolicy(scope=self.scope, authorized=True),
            dry_run=False,
            timeout=0.01,
        )

        self.assertEqual(result.status, "timeout")
        self.assertIsNone(result.returncode)


if __name__ == "__main__":
    unittest.main()
