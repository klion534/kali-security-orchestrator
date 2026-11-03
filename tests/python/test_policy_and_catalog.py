import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from kali_orchestrator.catalog import build_default_catalog
from kali_orchestrator.policy import AuthorizationError, ExecutionPolicy, TargetScope


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


if __name__ == "__main__":
    unittest.main()
