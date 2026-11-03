from dataclasses import dataclass


class AdapterError(ValueError):
    """Raised when a tool command cannot be built safely."""


@dataclass(frozen=True)
class CommandPlan:
    tool: str
    args: tuple[str, ...]
    manual: bool = False


class ToolAdapter:
    name = ""

    def build(self, target: str, artifacts_dir: str) -> CommandPlan:
        raise NotImplementedError


class NmapAdapter(ToolAdapter):
    name = "nmap"

    def build(self, target, artifacts_dir):
        return CommandPlan(self.name, ("-sV", "--version-light", "-T2", target))


class NucleiAdapter(ToolAdapter):
    name = "nuclei"

    def build(self, target, artifacts_dir):
        return CommandPlan(
            self.name,
            ("-u", target, "-jsonl", "-rate-limit", "5", "-bulk-size", "1", "-concurrency", "1"),
        )


class ZapAdapter(ToolAdapter):
    name = "owasp-zap"

    def build(self, target, artifacts_dir):
        return CommandPlan(self.name, ("-quickurl", target, "-quickprogress"))


class BurpAdapter(ToolAdapter):
    name = "burp-suite"

    def build(self, target, artifacts_dir):
        raise AdapterError("Burp Suite requires an explicit Professional/API integration")


class SqlmapAdapter(ToolAdapter):
    name = "sqlmap"

    def build(self, target, artifacts_dir):
        return CommandPlan(self.name, ("-u", target, "--batch", "--risk=1", "--level=1"))


class GitleaksAdapter(ToolAdapter):
    name = "gitleaks"

    def build(self, target, artifacts_dir):
        return CommandPlan(
            self.name,
            ("dir", "--redact", "--report-format", "json", "--report-path", f"{artifacts_dir}/gitleaks.json", target),
        )


class TrufflehogAdapter(ToolAdapter):
    name = "trufflehog"

    def build(self, target, artifacts_dir):
        return CommandPlan(self.name, ("filesystem", target, "--json", "--no-update"))


class TrivyAdapter(ToolAdapter):
    name = "trivy"

    def build(self, target, artifacts_dir):
        return CommandPlan(
            self.name,
            ("fs", "--format", "json", "--scanners", "vuln,secret,misconfig", target),
        )


class AdapterRegistry:
    def __init__(self, adapters=()):
        self._adapters = {adapter.name: adapter for adapter in adapters}

    def get(self, name: str) -> ToolAdapter:
        try:
            return self._adapters[name]
        except KeyError as error:
            raise AdapterError(f"no adapter registered for tool: {name}") from error


def build_default_adapters() -> AdapterRegistry:
    return AdapterRegistry(
        (
            NmapAdapter(),
            NucleiAdapter(),
            ZapAdapter(),
            BurpAdapter(),
            SqlmapAdapter(),
            GitleaksAdapter(),
            TrufflehogAdapter(),
            TrivyAdapter(),
        )
    )
