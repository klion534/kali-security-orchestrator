from dataclasses import dataclass
import ipaddress
from urllib.parse import urlsplit


class AuthorizationError(PermissionError):
    """Raised when a target or profile is outside the approved policy."""


@dataclass(frozen=True)
class TargetScope:
    domains: tuple[str, ...] = ()
    networks: tuple[ipaddress._BaseNetwork, ...] = ()

    @classmethod
    def from_values(cls, domains=(), networks=()):
        normalized_domains = tuple(
            value.strip().lower().removeprefix("*.")
            for value in domains
            if value and value.strip()
        )
        parsed_networks = tuple(ipaddress.ip_network(value, strict=False) for value in networks)
        if not normalized_domains and not parsed_networks:
            raise ValueError("at least one authorized domain or network is required")
        return cls(domains=normalized_domains, networks=parsed_networks)

    def allows(self, target: str) -> bool:
        hostname = _hostname(target)
        if not hostname:
            return False

        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            address = None

        if address is not None:
            return any(address in network for network in self.networks)

        return any(hostname == domain or hostname.endswith(f".{domain}") for domain in self.domains)


@dataclass(frozen=True)
class ExecutionPolicy:
    scope: TargetScope
    authorized: bool = False

    _elevated_profiles = frozenset({"active", "lab", "full"})

    def assert_can_run(self, profile: str, target: str) -> None:
        if not self.scope.allows(target):
            raise AuthorizationError(f"target is outside the authorized scope: {target}")
        if profile in self._elevated_profiles and not self.authorized:
            raise AuthorizationError(f"profile requires explicit authorization: {profile}")


def _hostname(target: str) -> str | None:
    value = target.strip()
    if not value or any(character in value for character in ("\n", "\r", "\x00")):
        return None
    parsed = urlsplit(value if "://" in value else f"//{value}")
    if parsed.username or parsed.password:
        return None
    try:
        return parsed.hostname.lower() if parsed.hostname else None
    except ValueError:
        return None
