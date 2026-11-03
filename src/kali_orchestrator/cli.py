import argparse
import json
import sys

from .catalog import build_default_catalog
from .config import ConfigError, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kali-orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="report catalog tool availability")
    doctor.set_defaults(handler=_doctor)

    plan = subparsers.add_parser("plan", help="validate an audit plan without executing tools")
    plan.add_argument("--config", required=True, help="path to a JSON audit plan")
    plan.set_defaults(handler=_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except ConfigError as error:
        print(f"configuration error: {error}", file=sys.stderr)
        return 2


def _doctor(_args) -> int:
    catalog = build_default_catalog()
    tools = []
    for name in sorted(catalog.names()):
        tool = catalog.get(name)
        tools.append(
            {
                "name": tool.name,
                "binary": tool.binary,
                "category": tool.category,
                "risk": tool.risk,
                "status": tool.status(),
                "executable": tool.executable(),
            }
        )
    print(json.dumps({"tools": tools}, indent=2))
    return 0


def _plan(args) -> int:
    config = load_config(args.config)
    catalog = build_default_catalog()
    tools = []
    for name in config.tools:
        tool = catalog.get(name)
        tools.append(
            {
                "name": tool.name,
                "category": tool.category,
                "risk": tool.risk,
                "status": tool.status(),
                "executable": tool.executable(),
            }
        )
    print(
        json.dumps(
            {
                "dry_run": True,
                "profile": config.profile,
                "authorized": config.authorized,
                "targets": list(config.targets),
                "tools": tools,
            },
            indent=2,
        )
    )
    return 0
