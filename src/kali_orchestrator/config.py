from dataclasses import dataclass
import json
from pathlib import Path

from .catalog import ToolCatalog, build_default_catalog
from .policy import AuthorizationError, ExecutionPolicy, TargetScope


class ConfigError(ValueError):
    """Raised when an audit plan is invalid or unsafe."""


PROFILES = frozenset({"passive", "safe-web", "authenticated", "code", "cloud", "mobile", "active", "lab", "full"})


@dataclass(frozen=True)
class AuditConfig:
    scope: TargetScope
    profile: str
    targets: tuple[str, ...]
    tools: tuple[str, ...]
    authorized: bool
    output_dir: str
    dry_run: bool = True


def load_config(path: str | Path, catalog: ToolCatalog | None = None) -> AuditConfig:
    source = Path(path)
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigError(f"cannot read configuration: {error}") from error

    if not isinstance(data, dict):
        raise ConfigError("configuration root must be an object")

    scope_data = data.get("scope")
    if not isinstance(scope_data, dict):
        raise ConfigError("scope must be an object")

    try:
        scope = TargetScope.from_values(
            domains=scope_data.get("domains", ()),
            networks=scope_data.get("networks", ()),
        )
    except (TypeError, ValueError) as error:
        raise ConfigError(f"invalid scope: {error}") from error

    profile = data.get("profile")
    if profile not in PROFILES:
        raise ConfigError(f"unsupported profile: {profile!r}")

    targets = _string_tuple(data.get("targets"), "targets")
    tools = _string_tuple(data.get("tools"), "tools")
    authorized = data.get("authorized", False)
    if not isinstance(authorized, bool):
        raise ConfigError("authorized must be a boolean")

    dry_run = data.get("dry_run", True)
    if dry_run is not True:
        raise ConfigError("dry_run must remain true until the execution runner is implemented")

    selected_catalog = catalog or build_default_catalog()
    unknown = sorted(set(tools) - selected_catalog.names())
    if unknown:
        raise ConfigError(f"unknown tools: {', '.join(unknown)}")

    policy = ExecutionPolicy(scope=scope, authorized=authorized)
    try:
        for target in targets:
            policy.assert_can_run(profile, target)
    except AuthorizationError as error:
        raise ConfigError(str(error)) from error

    output_dir = data.get("output_dir", "artifacts")
    if not isinstance(output_dir, str) or not output_dir.strip():
        raise ConfigError("output_dir must be a non-empty string")

    return AuditConfig(
        scope=scope,
        profile=profile,
        targets=targets,
        tools=tools,
        authorized=authorized,
        output_dir=output_dir,
        dry_run=dry_run,
    )


def _string_tuple(value, name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise ConfigError(f"{name} must be a non-empty list of strings")
    return tuple(item.strip() for item in value)
