#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPT_ROOT = Path(__file__).resolve().parent
OS_ROOT = SCRIPT_ROOT.parent
DOCS = OS_ROOT / "documents"
GUARD_SCRIPT = SCRIPT_ROOT / "agent-guard.py"
ORCHESTRATOR_SCRIPT = SCRIPT_ROOT / "orchestrator.py"
EXECUTOR_SCRIPT = SCRIPT_ROOT / "executor.py"
VERSION_FILE = DOCS / ".harnass-version.yaml"


def fail(message: str, code: int = 1) -> int:
    print(message, file=sys.stderr)
    return code


def load_script_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guard_module():
    return load_script_module(GUARD_SCRIPT, "harnass_guard")


def orchestrator_module():
    return load_script_module(ORCHESTRATOR_SCRIPT, "harnass_orchestrator")


def executor_module():
    return load_script_module(EXECUTOR_SCRIPT, "harnass_executor")


def command_check(args: argparse.Namespace) -> int:
    module = guard_module()
    command = args.command or "list"
    if command == "list":
        for name in sorted(module.COMMANDS):
            print(name)
        return 0
    if command == "all":
        return fail("check all is not supported; run 'check list' and choose a concrete guard command", 2)
    return module.main([GUARD_SCRIPT.name, command, *args.extra_args])


def command_status(_: argparse.Namespace) -> int:
    module = orchestrator_module()
    return module.main([ORCHESTRATOR_SCRIPT.name, "show"])


def command_sync(args: argparse.Namespace) -> int:
    module = orchestrator_module()
    argv = [ORCHESTRATOR_SCRIPT.name, "tick"]
    if args.stage:
        argv.append("--stage")
    return module.main(argv)


def command_version(_: argparse.Namespace) -> int:
    if not VERSION_FILE.is_file():
        return fail(f"missing version file: {VERSION_FILE}", 2)
    print(VERSION_FILE.read_text(encoding="utf-8").rstrip())
    return 0


def command_run_task(args: argparse.Namespace) -> int:
    module = executor_module()
    argv = [EXECUTOR_SCRIPT.name, "run-task"]
    if args.task_id:
        argv.extend(["--task-id", args.task_id])
    if args.no_commit:
        argv.append("--no-commit")
    return module.main(argv)


def command_run_milestone(args: argparse.Namespace) -> int:
    module = executor_module()
    argv = [EXECUTOR_SCRIPT.name, "run-milestone"]
    if args.milestone_id:
        argv.extend(["--milestone-id", args.milestone_id])
    if args.no_commit:
        argv.append("--no-commit")
    return module.main(argv)


def command_deploy_preview(args: argparse.Namespace) -> int:
    module = executor_module()
    argv = [EXECUTOR_SCRIPT.name, "deploy-preview"]
    if args.no_commit:
        argv.append("--no-commit")
    return module.main(argv)


def command_deploy_production(args: argparse.Namespace) -> int:
    module = executor_module()
    argv = [EXECUTOR_SCRIPT.name, "deploy-production"]
    if args.no_commit:
        argv.append("--no-commit")
    return module.main(argv)


def command_audit_final(args: argparse.Namespace) -> int:
    module = executor_module()
    argv = [EXECUTOR_SCRIPT.name, "audit-final"]
    if args.no_commit:
        argv.append("--no-commit")
    return module.main(argv)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Unified Harnass OS command wrapper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Run a concrete agent-guard command or list available commands.")
    check.add_argument("command", nargs="?", help="Guard command to run, or 'list' to print available commands.")
    check.add_argument(
        "extra_args", nargs=argparse.REMAINDER, help="Additional arguments forwarded to the guard command."
    )
    check.set_defaults(handler=command_check)

    status = subparsers.add_parser("status", help="Show the current orchestrator state.")
    status.set_defaults(handler=command_status)

    sync = subparsers.add_parser("sync", help="Recompute orchestrator state from repo documents.")
    sync.add_argument("--stage", action="store_true", help="Stage changed orchestrator-managed files.")
    sync.set_defaults(handler=command_sync)

    version = subparsers.add_parser("version", help="Print the current scaffold version document.")
    version.set_defaults(handler=command_version)

    run_task = subparsers.add_parser("run-task", help="Execute the next ready task or a specific task.")
    run_task.add_argument("--task-id", help="Explicit task id to execute.")
    run_task.add_argument("--no-commit", action="store_true", help="Run execution without creating a commit.")
    run_task.set_defaults(handler=command_run_task)

    run_milestone = subparsers.add_parser("run-milestone", help="Execute all tasks in the current or named milestone.")
    run_milestone.add_argument("--milestone-id", help="Explicit milestone id to execute.")
    run_milestone.add_argument("--no-commit", action="store_true", help="Run execution without creating a commit.")
    run_milestone.set_defaults(handler=command_run_milestone)

    deploy_preview = subparsers.add_parser("deploy-preview", help="Run the preview deployment route.")
    deploy_preview.add_argument("--no-commit", action="store_true", help="Run without creating a commit.")
    deploy_preview.set_defaults(handler=command_deploy_preview)

    deploy_production = subparsers.add_parser("deploy-production", help="Run the production deployment route.")
    deploy_production.add_argument("--no-commit", action="store_true", help="Run without creating a commit.")
    deploy_production.set_defaults(handler=command_deploy_production)

    audit_final = subparsers.add_parser("audit-final", help="Run the executable final audit route.")
    audit_final.add_argument("--no-commit", action="store_true", help="Run without creating a commit.")
    audit_final.set_defaults(handler=command_audit_final)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv[1:])
        return args.handler(args)
    except RuntimeError as exc:
        return fail(str(exc), 2)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
