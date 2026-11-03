from dataclasses import dataclass
import shutil


@dataclass(frozen=True)
class ToolSpec:
    name: str
    binary: str
    category: str
    risk: str
    profiles: tuple[str, ...]
    alternatives: tuple[str, ...] = ()

    def executable(self) -> str | None:
        for candidate in (self.binary, *self.alternatives):
            path = shutil.which(candidate)
            if path:
                return path
        return None

    def is_installed(self) -> bool:
        return self.executable() is not None

    def availability(self) -> str:
        return "installed" if self.is_installed() else "not-installed"

    def status(self) -> str:
        return "available" if self.is_installed() else "not-installed"


class ToolCatalog:
    def __init__(self, tools=()):
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> ToolSpec:
        return self._tools[name]

    def names(self) -> set[str]:
        return set(self._tools)

    def register(self, tool: ToolSpec) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool


def build_default_catalog() -> ToolCatalog:
    tools = [
        ToolSpec("nmap", "nmap", "network", "safe", ("passive", "safe-web", "active")),
        ToolSpec("nuclei", "nuclei", "web", "safe", ("passive", "safe-web", "authenticated", "active")),
        ToolSpec("owasp-zap", "zap.sh", "web", "safe", ("safe-web", "authenticated", "active")),
        ToolSpec("burp-suite", "burpsuite", "web", "safe", ("safe-web", "authenticated", "active"), ("burp",)),
        ToolSpec("sqlmap", "sqlmap", "web", "active", ("active", "lab")),
        ToolSpec("gitleaks", "gitleaks", "secrets", "safe", ("code", "full")),
        ToolSpec("trufflehog", "trufflehog", "secrets", "safe", ("code", "full")),
        ToolSpec("trivy", "trivy", "dependencies", "safe", ("code", "cloud", "full")),
        ToolSpec("amass", "amass", "recon", "passive", ("passive", "safe-web")),
        ToolSpec("subfinder", "subfinder", "recon", "passive", ("passive", "safe-web")),
        ToolSpec("httpx", "httpx", "recon", "safe", ("passive", "safe-web")),
        ToolSpec("ffuf", "ffuf", "web", "active", ("active", "lab")),
        ToolSpec("feroxbuster", "feroxbuster", "web", "active", ("active", "lab")),
        ToolSpec("nikto", "nikto", "web", "safe", ("safe-web", "active")),
        ToolSpec("testssl", "testssl.sh", "tls", "safe", ("passive", "safe-web"), ("testssl",)),
        ToolSpec("semgrep", "semgrep", "code", "safe", ("code", "full")),
        ToolSpec("osv-scanner", "osv-scanner", "dependencies", "safe", ("code", "cloud", "full")),
        ToolSpec("syft", "syft", "containers", "safe", ("code", "cloud")),
        ToolSpec("grype", "grype", "containers", "safe", ("code", "cloud")),
        ToolSpec("checkov", "checkov", "cloud", "safe", ("cloud", "full")),
        ToolSpec("prowler", "prowler", "cloud", "safe", ("cloud", "full")),
        ToolSpec("kube-bench", "kube-bench", "kubernetes", "safe", ("cloud", "full")),
        ToolSpec("mobsf", "mobsf", "mobile", "safe", ("mobile", "full")),
        ToolSpec("searchsploit", "searchsploit", "research", "lab", ("lab",)),
        ToolSpec("metasploit", "msfconsole", "exploitation", "lab", ("lab",)),
    ]
    return ToolCatalog(tools)
