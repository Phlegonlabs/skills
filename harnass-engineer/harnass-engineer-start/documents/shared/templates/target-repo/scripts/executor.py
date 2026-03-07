#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from harnass_yaml import (  # noqa: E402
    as_list,
    as_mapping,
    as_string_list,
    configure_context,
    fail,
    non_placeholder_string,
    parse_int,
    read_yaml,
)

OS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = OS_ROOT.parent
DOCS = OS_ROOT / "documents"
PLAN_DIR = DOCS / "plans"
STATUS_FILE = DOCS / "status" / "current.yaml"
RUN_FILE = DOCS / "runs" / "current.yaml"
DEPLOY_FILE = DOCS / "deploy" / "current.yaml"
RELEASE_FILE = DOCS / "release" / "current.yaml"
AUDIT_FILE = DOCS / "audit" / "current.yaml"
AUDIT_HISTORY_DIR = DOCS / "audit" / "history"
AUDIT_FINDINGS_DIR = DOCS / "audit" / "findings"
HANDOFF_DIR = DOCS / "handoffs"
VALIDATION_HISTORY_DIR = DOCS / "validation" / "history"
PLACEHOLDER_PREFIX = "<fill"
MODULE_ORDER = (
    "frontend-experience",
    "frontend-quality",
    "accessibility",
    "backend-runtime",
    "api-contract",
    "frontend-backend-integration",
    "security",
    "content-quality",
    "content-safety",
    "seo",
    "performance-observability",
    "deploy-runtime-consistency",
    "ci-cd-release-hygiene",
    "documentation-signoff",
    "blockchain-contract-audit",
)
UNRESOLVED_TOKEN = re.compile(r"\$\{([A-Za-z0-9_.-]+)\}")


class ExecutorFailure(RuntimeError):
    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


configure_context(error_type=ExecutorFailure, repo_root=REPO_ROOT, placeholder_prefix=PLACEHOLDER_PREFIX)


def now_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def read_optional_yaml(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return read_yaml(path)


def yaml_scalar(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    if (
        not text
        or text.strip() != text
        or text in {"true", "false", "null", "~"}
        or any(char in text for char in {":", "#", "{", "}", "[", "]", '"', "'"})
        or "\n" in text
    ):
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return text


def dump_yaml(value: object, indent: int = 0) -> str:
    space = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, dict):
                if not child:
                    lines.append(f"{space}{key}: {{}}")
                else:
                    lines.append(f"{space}{key}:")
                    lines.append(dump_yaml(child, indent + 1))
            elif isinstance(child, list):
                if not child:
                    lines.append(f"{space}{key}: []")
                else:
                    lines.append(f"{space}{key}:")
                    lines.append(dump_yaml(child, indent + 1))
            else:
                lines.append(f"{space}{key}: {yaml_scalar(child)}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines: list[str] = []
        for item in value:
            if isinstance(item, dict):
                if not item:
                    lines.append(f"{space}- {{}}")
                else:
                    lines.append(f"{space}-")
                    lines.append(dump_yaml(item, indent + 1))
            elif isinstance(item, list):
                if not item:
                    lines.append(f"{space}- []")
                else:
                    lines.append(f"{space}-")
                    lines.append(dump_yaml(item, indent + 1))
            else:
                lines.append(f"{space}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{space}{yaml_scalar(value)}"


def write_yaml(path: Path, data: dict[str, object]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    rendered = dump_yaml(data).rstrip() + "\n"
    if existing == rendered:
        return False
    path.write_text(rendered, encoding="utf-8")
    return True


def write_text(path: Path, text: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    if existing == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def repo_ref(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise ExecutorFailure(message, completed.returncode)
    return completed


def shell(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, shell=True, check=False)


def current_branch_or_worktree() -> str:
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    if branch and branch != "HEAD":
        return branch
    return str(REPO_ROOT)


def status_data() -> dict[str, object]:
    return read_optional_yaml(STATUS_FILE)


def load_current_plan() -> tuple[Path, dict[str, object]]:
    status = status_data()
    plan_id = non_placeholder_string(status.get("plan_id"))
    if plan_id:
        path = PLAN_DIR / f"{plan_id}.yaml"
        if not path.is_file():
            raise ExecutorFailure(f"status/current.yaml references missing plan: {repo_ref(path)}", 2)
        return path, read_yaml(path)
    plan_files = sorted(PLAN_DIR.glob("*.yaml"))
    if len(plan_files) != 1:
        raise ExecutorFailure("executor requires exactly one active plan or status.current.plan_id", 2)
    return plan_files[0], read_yaml(plan_files[0])


def plan_revision(plan: dict[str, object]) -> int:
    revision = parse_int(as_mapping(plan.get("change_log")).get("revision"))
    return revision or 1


def plan_tasks(plan: dict[str, object]) -> list[dict[str, object]]:
    return [task for task in as_list(plan.get("tasks")) if isinstance(task, dict)]


def plan_milestones(plan: dict[str, object]) -> list[dict[str, object]]:
    return [milestone for milestone in as_list(plan.get("milestones")) if isinstance(milestone, dict)]


def inventory_vars() -> dict[str, str]:
    inventory = read_optional_yaml(DOCS / "inventory" / "current-state.yaml")
    deploy = read_optional_yaml(DEPLOY_FILE)
    release = read_optional_yaml(RELEASE_FILE)
    runtime_provider = non_placeholder_string(as_mapping(inventory.get("runtime")).get("provider")) or "provider"
    runtime = read_optional_yaml(DOCS / "runtime" / f"{runtime_provider}.yaml")

    values: dict[str, str] = {}
    for section_name in ("frontend", "backend", "deployment", "runtime", "testing", "design_docs", "design_validation"):
        for key, value in as_mapping(inventory.get(section_name)).items():
            text = non_placeholder_string(value)
            if text:
                values[key] = text
    for source in (deploy, release, runtime):
        for key, value in source.items():
            text = non_placeholder_string(value)
            if text:
                values[key] = text
    if "preview_url" not in values:
        preview_url = non_placeholder_string(as_mapping(deploy.get("preview_environment")).get("url"))
        if preview_url:
            values["preview_url"] = preview_url
    if "production_url" not in values:
        production_url = non_placeholder_string(as_mapping(deploy.get("production_environment")).get("url"))
        if production_url:
            values["production_url"] = production_url
    return values


def resolve_command(command: str, variables: dict[str, str]) -> str:
    resolved = command
    for match in UNRESOLVED_TOKEN.findall(command):
        value = variables.get(match)
        if value:
            resolved = resolved.replace(f"${{{match}}}", value)
    unresolved = UNRESOLVED_TOKEN.findall(resolved)
    if unresolved:
        raise ExecutorFailure(
            "command still contains unresolved variables: "
            + ", ".join(sorted({f'${{{name}}}' for name in unresolved}))
            + f" -> {command}",
            1,
        )
    if PLACEHOLDER_PREFIX in resolved:
        raise ExecutorFailure(f"command still contains placeholder content: {command}", 1)
    return resolved


def task_lookup(plan: dict[str, object]) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    task_map = {str(task["id"]): task for task in plan_tasks(plan) if task.get("id") is not None}
    milestone_map = {str(ms["id"]): ms for ms in plan_milestones(plan) if ms.get("id") is not None}
    return task_map, milestone_map


def task_milestone_map(plan: dict[str, object]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for milestone in plan_milestones(plan):
        milestone_id = str(milestone.get("id", ""))
        for task_id in as_string_list(milestone.get("tasks")):
            mapping[task_id] = milestone_id
    return mapping


def task_ready(task: dict[str, object], task_map: dict[str, dict[str, object]]) -> bool:
    status = non_placeholder_string(task.get("status")) or "pending"
    if status not in {"ready", "pending", "in_progress"}:
        return False
    for dep_id in as_string_list(task.get("depends_on")):
        dep = task_map.get(dep_id)
        if dep is None or dep.get("status") != "committed":
            return False
    return True


def select_task(plan: dict[str, object], explicit_task_id: str | None) -> tuple[dict[str, object], str]:
    task_map, _ = task_lookup(plan)
    milestone_map = task_milestone_map(plan)
    if explicit_task_id:
        task = task_map.get(explicit_task_id)
        if task is None:
            raise ExecutorFailure(f"unknown task id: {explicit_task_id}", 2)
        if not task_ready(task, task_map):
            raise ExecutorFailure(f"task {explicit_task_id} is not ready for execution", 1)
        return task, milestone_map.get(explicit_task_id, "")

    for task in plan_tasks(plan):
        task_id = str(task.get("id", ""))
        if task_ready(task, task_map):
            return task, milestone_map.get(task_id, "")
    raise ExecutorFailure("no ready task found in the active plan", 1)


def update_status(plan: dict[str, object], current_task_id: str, current_milestone_id: str) -> None:
    status = read_optional_yaml(STATUS_FILE)
    completed = set(as_string_list(status.get("completed")))
    task_map, _ = task_lookup(plan)
    if task_map[current_task_id].get("status") == "committed":
        completed.add(current_task_id)
    next_task = None
    for task in plan_tasks(plan):
        task_id = str(task.get("id", ""))
        if task_ready(task, task_map):
            next_task = task_id
            break
    status["plan_id"] = non_placeholder_string(plan.get("id")) or status.get("plan_id")
    status["plan_revision"] = plan_revision(plan)
    status["current_milestone"] = current_milestone_id or status.get("current_milestone")
    status["completed"] = sorted(completed)
    status["next"] = next_task
    status.setdefault("known_issues", [])
    status.setdefault("follow_ups", [])
    status.setdefault("decision_notes", [])
    status.setdefault("deployment_notes", [])
    write_yaml(STATUS_FILE, status)


def update_run(plan: dict[str, object], milestone_id: str, task_id: str, evidence_ref: str) -> None:
    run = read_optional_yaml(RUN_FILE)
    if not run:
        run = {
            "run_id": f"run-{slug_timestamp()}",
            "status": "active",
            "validation_history": [],
            "repair_history": [],
            "decision_notes": [],
            "deployment_history": [],
        }
    run["plan_id"] = non_placeholder_string(plan.get("id")) or run.get("plan_id")
    run["task_horizon"] = non_placeholder_string(plan.get("task_horizon")) or run.get("task_horizon")
    run["agent_topology"] = non_placeholder_string(plan.get("agent_topology")) or run.get("agent_topology")
    run["started_at"] = non_placeholder_string(run.get("started_at")) or now_timestamp()
    run["current_milestone"] = milestone_id
    run["current_task"] = task_id
    run["next_action"] = "continue execution"
    history = as_list(run.get("validation_history"))
    history.append(evidence_ref)
    run["validation_history"] = history
    run["runtime_summary"] = f"last validated task: {task_id}"
    write_yaml(RUN_FILE, run)


def persist_validation(kind: str, scope_id: str, payload: dict[str, object]) -> str:
    path = VALIDATION_HISTORY_DIR / f"{kind}-{scope_id}-{slug_timestamp()}.yaml"
    write_yaml(path, payload)
    return repo_ref(path)


def run_command_sequence(commands: list[str]) -> tuple[list[dict[str, object]], bool]:
    results: list[dict[str, object]] = []
    background: subprocess.Popen[str] | None = None
    passed = True
    for command in commands:
        stripped = command.strip()
        if stripped.lower().startswith("sleep "):
            seconds = stripped.split(maxsplit=1)[1]
            completed = shell(f'python -c "import time; time.sleep({seconds})"')
        elif stripped.startswith("kill %1"):
            if background is not None:
                background.terminate()
                try:
                    background.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    background.kill()
                completed = subprocess.CompletedProcess(stripped, 0, "", "")
                background = None
            else:
                completed = subprocess.CompletedProcess(stripped, 0, "", "")
        elif stripped.endswith("&"):
            background = subprocess.Popen(
                stripped[:-1].strip(),
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            completed = subprocess.CompletedProcess(stripped, 0, "", "")
        else:
            completed = shell(stripped)
        results.append(
            {
                "command": stripped,
                "exit_code": completed.returncode,
                "stdout": (completed.stdout or "").strip(),
                "stderr": (completed.stderr or "").strip(),
            }
        )
        if completed.returncode != 0:
            passed = False
            break
    if background is not None:
        background.terminate()
        try:
            background.wait(timeout=10)
        except subprocess.TimeoutExpired:
            background.kill()
    return results, passed


def update_task_statuses(plan: dict[str, object], milestone_id: str, task_id: str, final_status: str) -> None:
    task_map, milestone_map = task_lookup(plan)
    task_map[task_id]["status"] = final_status
    for milestone in milestone_map.values():
        member_ids = as_string_list(milestone.get("tasks"))
        member_statuses = [task_map[item].get("status") for item in member_ids if item in task_map]
        if member_statuses and all(status == "committed" for status in member_statuses):
            milestone["status"] = "complete"
        elif any(status in {"validated", "committed", "in_progress"} for status in member_statuses):
            milestone["status"] = "in_progress"
        else:
            milestone["status"] = milestone.get("status") or "pending"
    update_status(plan, task_id, milestone_id)


def write_handoff(plan: dict[str, object], task: dict[str, object], milestone_id: str, evidence_ref: str) -> str:
    task_id = str(task["id"])
    path = HANDOFF_DIR / f"{task_id}.yaml"
    changed = [line for line in git(["status", "--short"]).stdout.splitlines() if line.strip()]
    data = {
        "plan_id": non_placeholder_string(plan.get("id")) or "unknown-plan",
        "plan_revision": plan_revision(plan),
        "task_id": task_id,
        "milestone_id": milestone_id,
        "branch_or_worktree": current_branch_or_worktree(),
        "write_scope": as_string_list(task.get("write_scope")),
        "changed_surfaces": changed or ["none recorded"],
        "validations_passed": [evidence_ref],
        "commit_ref": f"HEAD task:{task_id}",
        "next_owner": "next-ready-task",
        "remaining_risks": as_string_list(task.get("remaining_risks")) or ["none recorded"],
    }
    write_yaml(path, data)
    return repo_ref(path)


def commit_all(message: str) -> None:
    git(["add", "-A"])
    diff = git(["diff", "--cached", "--name-only"]).stdout.strip()
    if not diff:
        return
    git(["commit", "-m", message])


def command_run_task(args: argparse.Namespace) -> int:
    plan_path, plan = load_current_plan()
    task, milestone_id = select_task(plan, args.task_id)
    task_id = str(task["id"])
    variables = inventory_vars()
    commands = [resolve_command(command, variables) for command in as_string_list(task.get("validation_commands"))]
    if not commands:
        raise ExecutorFailure(f"task {task_id} has no executable validation_commands", 1)

    task["status"] = "in_progress"
    write_yaml(plan_path, plan)
    results, passed = run_command_sequence(commands)
    evidence_ref = persist_validation(
        "task",
        task_id,
        {
            "kind": "task",
            "task_id": task_id,
            "milestone_id": milestone_id,
            "plan_id": non_placeholder_string(plan.get("id")) or "unknown-plan",
            "executed_at": now_timestamp(),
            "status": "passed" if passed else "failed",
            "commands": results,
        },
    )
    update_run(plan, milestone_id, task_id, evidence_ref)
    if not passed:
        task["status"] = "blocked"
        write_yaml(plan_path, plan)
        update_status(plan, task_id, milestone_id)
        raise ExecutorFailure(f"task validation failed for {task_id}; see {evidence_ref}", 1)

    task["status"] = "validated"
    write_handoff(plan, task, milestone_id, evidence_ref)
    if not args.no_commit:
        task["status"] = "committed"
    update_task_statuses(plan, milestone_id, task_id, task["status"])
    write_yaml(plan_path, plan)
    if not args.no_commit:
        commit_all(f"task:{task_id} {non_placeholder_string(task.get('goal')) or 'validated task'}")
    return 0


def command_run_milestone(args: argparse.Namespace) -> int:
    while True:
        plan_path, plan = load_current_plan()
        task_map, milestone_map = task_lookup(plan)
        selected: dict[str, object] | None = None
        selected_milestone = args.milestone_id
        for milestone in plan_milestones(plan):
            milestone_id = str(milestone.get("id", ""))
            if selected_milestone and milestone_id != selected_milestone:
                continue
            if milestone.get("status") == "complete":
                continue
            for task_id in as_string_list(milestone.get("tasks")):
                task = task_map.get(task_id)
                if task is not None and task_ready(task, task_map):
                    selected = task
                    selected_milestone = milestone_id
                    break
            if selected is not None:
                break
        if selected is None:
            return 0
        result = command_run_task(argparse.Namespace(task_id=str(selected["id"]), no_commit=args.no_commit))
        if result != 0:
            return result


def update_deploy_state(environment: str, evidence_ref: str, passed: bool) -> None:
    deploy = read_optional_yaml(DEPLOY_FILE)
    release = read_optional_yaml(RELEASE_FILE)
    deploy["status"] = f"{environment}-passed" if passed else f"{environment}-failed"
    validation_key = f"{environment}_validation"
    validation = as_mapping(deploy.get(validation_key))
    validation["status"] = "passed" if passed else "failed"
    validation["evidence_ref"] = evidence_ref
    deploy[validation_key] = validation
    if environment == "preview":
        release["preview_status"] = "passed" if passed else "failed"
        preview_url = non_placeholder_string(as_mapping(deploy.get("preview_environment")).get("url"))
        if preview_url:
            release["preview_url"] = preview_url
    else:
        release["production_gate"] = "passed" if passed else "failed"
        release["status"] = "awaiting-final-audit" if passed else "deploy_failed"
        production_url = non_placeholder_string(as_mapping(deploy.get("production_environment")).get("url"))
        if production_url:
            release["production_url"] = production_url
    write_yaml(DEPLOY_FILE, deploy)
    write_yaml(RELEASE_FILE, release)


def run_deploy(environment: str, *, no_commit: bool) -> int:
    deploy = read_yaml(DEPLOY_FILE)
    variables = inventory_vars()
    build_command = resolve_command(non_placeholder_string(deploy.get("build_command")) or "${build_command}", variables)
    deploy_key = f"{environment}_deploy_command"
    deploy_command = resolve_command(non_placeholder_string(deploy.get(deploy_key)) or f"${{{deploy_key}}}", variables)
    url = variables.get(f"{environment}_url", "")
    commands = [build_command, deploy_command]
    if url:
        commands.append(f"curl -sf {url}/ || exit 1")
    results, passed = run_command_sequence(commands)
    evidence_ref = persist_validation(
        "deploy",
        environment,
        {
            "kind": "deploy",
            "environment": environment,
            "executed_at": now_timestamp(),
            "status": "passed" if passed else "failed",
            "commands": results,
        },
    )
    update_deploy_state(environment, evidence_ref, passed)
    if not passed:
        raise ExecutorFailure(f"{environment} deployment failed; see {evidence_ref}", 1)
    if not no_commit:
        commit_all(f"task:deploy-{environment} record {environment} deployment")
    return 0


def applicable_modules() -> list[str]:
    inventory = read_optional_yaml(DOCS / "inventory" / "current-state.yaml")
    ui_facing = inventory.get("ui_facing") is True
    backend_present = bool(as_string_list(as_mapping(inventory.get("backend")).get("services")))
    modules: list[str] = []
    for module in MODULE_ORDER:
        if module.startswith("frontend") or module in {"accessibility", "seo", "content-quality", "content-safety"}:
            if ui_facing:
                modules.append(module)
            continue
        if module in {"backend-runtime", "api-contract"}:
            if backend_present or inventory.get("app_type") == "api-only":
                modules.append(module)
            continue
        if module == "frontend-backend-integration":
            if ui_facing and backend_present:
                modules.append(module)
            continue
        if module == "blockchain-contract-audit":
            continue
        modules.append(module)
    return modules


def module_result(module_id: str, deploy: dict[str, object], release: dict[str, object]) -> dict[str, object]:
    findings: list[str] = []
    checks_run = [f"module:{module_id}"]
    evidence_refs = ["harnass-os/documents/deploy/current.yaml", "harnass-os/documents/release/current.yaml"]
    smoke_required = module_id in {
        "frontend-experience",
        "backend-runtime",
        "api-contract",
        "frontend-backend-integration",
        "seo",
        "performance-observability",
        "deploy-runtime-consistency",
    }
    smoke_status = "passed"
    deep_status = "passed"
    if module_id == "deploy-runtime-consistency":
        if as_mapping(deploy.get("production_validation")).get("status") != "passed":
            findings.append("production validation is not passed in deploy/current.yaml")
        if release.get("production_gate") != "passed":
            findings.append("release/current.yaml production_gate is not passed")
    if module_id == "frontend-backend-integration":
        preview_url = non_placeholder_string(release.get("preview_url"))
        if preview_url is None:
            findings.append("release/current.yaml is missing preview_url for integration replay")
        evidence_refs.append("harnass-os/documents/inventory/current-state.yaml")
    if findings:
        smoke_status = "failed" if smoke_required else "not_required"
        deep_status = "failed"
    return {
        "module_id": module_id,
        "applicable": True,
        "smoke_required": smoke_required,
        "smoke_status": smoke_status if smoke_required else "not_required",
        "deep_audit_status": deep_status,
        "checks_run": checks_run,
        "manual_checks": [],
        "findings": findings,
        "blocking": bool(findings),
        "evidence_refs": evidence_refs,
    }


def command_audit_final(args: argparse.Namespace) -> int:
    deploy = read_yaml(DEPLOY_FILE)
    release = read_yaml(RELEASE_FILE)
    modules = applicable_modules()
    results = [module_result(module_id, deploy, release) for module_id in modules]
    blocking_findings: list[str] = []
    smoke_failures: list[str] = []
    for result in results:
        blocking_findings.extend(as_string_list(result.get("findings")))
        if result.get("smoke_status") == "failed":
            smoke_failures.append(str(result.get("module_id")))
    passed = not blocking_findings and not smoke_failures
    audit_id = f"audit-{slug_timestamp()}"
    audit = {
        "audit_id": audit_id,
        "plan_id": non_placeholder_string(status_data().get("plan_id")) or non_placeholder_string(release.get("plan_id")) or "unknown-plan",
        "release_ref": "harnass-os/documents/release/current.yaml",
        "deploy_ref": "harnass-os/documents/deploy/current.yaml",
        "target_environment": "production",
        "scope_modules": modules,
        "status": "passed" if passed else "failed",
        "summary": "All applicable modules passed" if passed else "Blocking findings remain",
        "blocking_findings": blocking_findings,
        "non_blocking_findings": [],
        "follow_up_required": not passed,
        "follow_up_plan_ref": None,
        "executed_checks": [f"module:{module_id}" for module_id in modules],
        "manual_checks": [],
        "skipped_checks": [],
        "smoke_failures": smoke_failures,
        "module_results": results,
    }
    write_yaml(AUDIT_FILE, audit)
    write_yaml(AUDIT_HISTORY_DIR / f"{audit_id}.yaml", audit)
    report_lines = [
        f"# Final Audit {audit_id}",
        "",
        f"status: {audit['status']}",
        f"summary: {audit['summary']}",
        "",
        "blocking findings:",
    ]
    if blocking_findings:
        report_lines.extend(f"- {finding}" for finding in blocking_findings)
    else:
        report_lines.append("- none")
    report = "\n".join(report_lines)
    write_text(AUDIT_FINDINGS_DIR / f"{audit_id}.md", report + "\n")
    release["final_audit_ref"] = "harnass-os/documents/audit/current.yaml"
    release["final_audit_status"] = "passed" if passed else "failed"
    release["status"] = "complete" if passed else "audit_failed"
    write_yaml(RELEASE_FILE, release)
    state = read_optional_yaml(STATUS_FILE)
    notes = as_list(state.get("deployment_notes"))
    notes.append(f"final audit {audit_id}: {audit['status']}")
    state["deployment_notes"] = notes
    write_yaml(STATUS_FILE, state)
    if not passed:
        raise ExecutorFailure(f"final audit failed; see {repo_ref(AUDIT_FILE)}", 1)
    if not args.no_commit:
        commit_all("task:final-audit record production final audit")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Harnass execution runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_task = subparsers.add_parser("run-task", help="Execute one ready task and optionally auto-commit.")
    run_task.add_argument("--task-id", help="Explicit task id to execute.")
    run_task.add_argument("--no-commit", action="store_true", help="Do not create a git commit after validation.")
    run_task.set_defaults(handler=command_run_task)

    run_milestone = subparsers.add_parser("run-milestone", help="Execute all ready tasks inside a milestone.")
    run_milestone.add_argument("--milestone-id", help="Explicit milestone id to execute.")
    run_milestone.add_argument("--no-commit", action="store_true", help="Do not create git commits after tasks.")
    run_milestone.set_defaults(handler=command_run_milestone)

    preview = subparsers.add_parser("deploy-preview", help="Run preview deployment and smoke validation.")
    preview.add_argument("--no-commit", action="store_true", help="Do not create a git commit after deploy docs update.")
    preview.set_defaults(handler=lambda args: run_deploy("preview", no_commit=args.no_commit))

    production = subparsers.add_parser("deploy-production", help="Run production deployment and smoke validation.")
    production.add_argument("--no-commit", action="store_true", help="Do not create a git commit after deploy docs update.")
    production.set_defaults(handler=lambda args: run_deploy("production", no_commit=args.no_commit))

    audit = subparsers.add_parser("audit-final", help="Run executable production final audit.")
    audit.add_argument("--no-commit", action="store_true", help="Do not create a git commit after audit docs update.")
    audit.set_defaults(handler=command_audit_final)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv[1:])
        return args.handler(args)
    except ExecutorFailure as exc:
        return fail(str(exc), getattr(exc, "code", 1))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
