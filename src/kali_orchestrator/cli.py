import argparse
import json
import sys

from .catalog import build_default_catalog
from .config import ConfigError, load_config
from .policy import ExecutionPolicy
from .runner import RunnerError, ToolRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kali-orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="report catalog tool availability")
    doctor.set_defaults(handler=_doctor)

    plan = subparsers.add_parser("plan", help="validate an audit plan without executing tools")
    plan.add_argument("--config", required=True, help="path to a JSON audit plan")
    plan.set_defaults(handler=_plan)

    run = subparsers.add_parser("run", help="execute one registered tool with explicit authorization")
    run.add_argument("--config", required=True, help="path to a JSON audit plan")
    run.add_argument("--tool", required=True, help="registered tool name")
    run.add_argument("--target", required=True, help="target already present in the plan")
    run.add_argument("--execute", action="store_true", help="confirm real execution")
    run.add_argument("--timeout", type=float, default=300.0)
    run.add_argument("--arg", action="append", default=[], help="argument passed as one argv item")
    run.set_defaults(handler=_run)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ConfigError, RunnerError) as error:
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


def _run(args) -> int:
    config = load_config(args.config)
    if not args.execute:
        raise RunnerError("real execution requires the explicit --execute flag")
    if config.dry_run:
        raise RunnerError("configuration dry_run must be false for real execution")
    if args.target not in config.targets:
        raise RunnerError("target is not listed in the configuration")
    if args.tool not in config.tools:
        raise RunnerError("tool is not listed in the configuration")

    result = ToolRunner(build_default_catalog()).run(
        args.tool,
        profile=config.profile,
        target=args.target,
        args=args.arg,
        policy=ExecutionPolicy(scope=config.scope, authorized=config.authorized),
        dry_run=False,
        timeout=args.timeout,
    )
    print(json.dumps(result.as_dict(), indent=2))
    return 0 if result.status == "completed" else 1
