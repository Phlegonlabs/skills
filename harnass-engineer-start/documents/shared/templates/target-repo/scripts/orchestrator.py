#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from copy import deepcopy
from datetime import UTC, datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import NamedTuple

sys.dont_write_bytecode = True

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
    parse_yaml_subset,
    read_yaml,
)

OS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = OS_ROOT.parent
DOCS = OS_ROOT / "documents"
ORCHESTRATOR_FILE = DOCS / "orchestrator" / "current.yaml"
PLAN_DIR = DOCS / "plans"
STATUS_FILE = DOCS / "status" / "current.yaml"
RUN_LEDGER_FILE = DOCS / "runs" / "current.yaml"
DEPLOY_FILE = DOCS / "deploy" / "current.yaml"
RELEASE_FILE = DOCS / "release" / "current.yaml"
AUDIT_FILE = DOCS / "audit" / "current.yaml"
CHANGE_REQUEST_FILE = DOCS / "intake" / "change-requests" / "current.yaml"
REPLAN_REQUEST_FILE = DOCS / "intake" / "re-plan-requests" / "current.yaml"
TRACKER_FILE = PLAN_DIR / "milestone-tasks.md"
GUARD_FILE = OS_ROOT / "scripts" / "agent-guard.py"
PLACEHOLDER_PREFIX = "<fill"
DONE_SMOKE_STATUSES = {"passed", "not_required", "skipped"}
DONE_DEEP_STATUSES = {"passed", "skipped"}
SYNC_LANES = {"none", "inferred_drift", "user_change_request", "re_plan_request", "manual_triage"}
SYNC_STATUSES = {"clean", "needs_review", "applying_followup", "needs_replan", "needs_human_triage"}
STANDARD_EXECUTION_READY_FIELDS = (
    "self_review_passed",
    "horizon_confirmed",
    "task_docs_synced",
    "tasks_have_entrypoints",
    "tasks_have_implementation_steps",
    "tasks_have_validation_commands",
)
TRACKED_CHANGE_TARGETS = (
    "src",
    "app",
    "pages",
    "components",
    "package.json",
    "tsconfig.json",
    "wrangler.toml",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    ".env.example",
)
BOOTSTRAP_SENTINELS = (
    REPO_ROOT / "Architecture.md",
    DOCS / "routes" / "router.yaml",
    STATUS_FILE,
    GUARD_FILE,
)
BUILTIN_STATES = {"IDLE", "COMPLETE", "BLOCKED"}


def _load_known_states() -> set[str]:
    """Load registered phases from orchestrator config, falling back to builtins."""
    phases = set(BUILTIN_STATES)
    if ORCHESTRATOR_FILE.is_file():
        data = read_yaml(ORCHESTRATOR_FILE)
        registered = as_string_list(as_list(data.get("registered_phases")))
        if registered:
            phases.update(registered)
    if not phases - BUILTIN_STATES:
        phases.update({
            "STARTING", "READY_FOR_PLAN", "PLANNING", "PLAN_REVIEW",
            "IMPLEMENTING", "DEPLOYING", "FINAL_AUDITING",
        })
    return phases


class OrchestratorFailure(RuntimeError):
    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


class SyncResult(NamedTuple):
    changed_files: list[Path]
    lane: str
    transition_note: str | None
    last_plan_sync_at: str | None


configure_context(error_type=OrchestratorFailure, repo_root=REPO_ROOT, placeholder_prefix=PLACEHOLDER_PREFIX)


def now_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_mapping(parent: dict[str, object], key: str) -> dict[str, object]:
    current = parent.get(key)
    if isinstance(current, dict):
        return current
    created: dict[str, object] = {}
    parent[key] = created
    return created


def ensure_list(parent: dict[str, object], key: str) -> list[object]:
    current = parent.get(key)
    if isinstance(current, list):
        return current
    created: list[object] = []
    parent[key] = created
    return created


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
        lines = []
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
    existing_data: object | None = None
    if path.is_file():
        existing_text = path.read_text(encoding="utf-8")
        try:
            existing_data = parse_yaml_subset(existing_text)
        except OrchestratorFailure:
            existing_data = None
    if existing_data == data:
        return False
    path.write_text(dump_yaml(data).rstrip() + "\n", encoding="utf-8")
    return True


def write_text(path: Path, text: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    if existing == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def default_state() -> dict[str, object]:
    return {
        "state": "IDLE",
        "previous_stable_state": "IDLE",
        "active_plan_id": None,
        "active_plan_revision": None,
        "release_affecting": False,
        "current_task_id": None,
        "current_audit_module": None,
        "completed_audit_modules": [],
        "pending_events": [],
        "observed_changes": [],
        "sync_lane": "none",
        "sync_status": "clean",
        "affected_task_ids": [],
        "pending_change_request_ids": [],
        "pending_replan_request_ids": [],
        "pending_triage_request_ids": [],
        "last_plan_sync_at": None,
        "last_transition": "initialized",
        "last_error": None,
        "updated_at": None,
    }


def load_orchestrator_state() -> dict[str, object]:
    state = default_state()
    if ORCHESTRATOR_FILE.is_file():
        state.update(read_yaml(ORCHESTRATOR_FILE))
    known_states = _load_known_states()
    current_state = non_placeholder_string(state.get("state")) or "IDLE"
    if current_state not in known_states:
        current_state = "IDLE"
    previous_stable = non_placeholder_string(state.get("previous_stable_state")) or current_state
    if previous_stable not in known_states or previous_stable == "BLOCKED":
        previous_stable = "IDLE"
    sync_lane = non_placeholder_string(state.get("sync_lane")) or "none"
    if sync_lane not in SYNC_LANES:
        sync_lane = "none"
    sync_status = non_placeholder_string(state.get("sync_status")) or "clean"
    if sync_status not in SYNC_STATUSES:
        sync_status = "clean"

    state["state"] = current_state
    state["previous_stable_state"] = previous_stable
    state["sync_lane"] = sync_lane
    state["sync_status"] = sync_status
    state["completed_audit_modules"] = [
        str(item) for item in as_list(state.get("completed_audit_modules")) if str(item).strip()
    ]
    state["pending_events"] = [str(item) for item in as_list(state.get("pending_events")) if str(item).strip()]
    state["observed_changes"] = [str(item) for item in as_list(state.get("observed_changes")) if str(item).strip()]
    state["affected_task_ids"] = [str(item) for item in as_list(state.get("affected_task_ids")) if str(item).strip()]
    state["pending_change_request_ids"] = [
        str(item) for item in as_list(state.get("pending_change_request_ids")) if str(item).strip()
    ]
    state["pending_replan_request_ids"] = [
        str(item) for item in as_list(state.get("pending_replan_request_ids")) if str(item).strip()
    ]
    state["pending_triage_request_ids"] = [
        str(item) for item in as_list(state.get("pending_triage_request_ids")) if str(item).strip()
    ]
    return state


def git_output(*args: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def stage_files(paths: list[Path]) -> None:
    unique: list[str] = []
    seen: set[str] = set()
    for path in paths:
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if relative_path in seen:
            continue
        seen.add(relative_path)
        unique.append(relative_path)
    if not unique:
        return
    result = subprocess.run(
        ["git", "add", "--", *unique],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise OrchestratorFailure(result.stdout + result.stderr, 2)


def bootstrap_ready() -> bool:
    return all(path.exists() for path in BOOTSTRAP_SENTINELS)


def bootstrap_history_exists() -> bool:
    return any((DOCS / "runs" / "history").glob("bootstrap-*.yaml"))


def normalize_repo_path(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def slugify(value: str) -> str:
    lowered = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return lowered or "follow-up"


def current_plan_pointer() -> tuple[str | None, int | None]:
    status = read_optional_yaml(STATUS_FILE)
    plan_id = non_placeholder_string(status.get("plan_id"))
    revision = parse_int(status.get("plan_revision"))
    return plan_id, revision


def select_plan() -> tuple[Path | None, dict[str, object]]:
    plan_id, _ = current_plan_pointer()
    if plan_id:
        path = PLAN_DIR / f"{plan_id}.yaml"
        if path.is_file():
            return path, read_yaml(path)

    plan_paths = sorted(PLAN_DIR.glob("*.yaml"))
    if not plan_paths:
        return None, {}
    selected = max(plan_paths, key=lambda candidate: candidate.stat().st_mtime)
    return selected, read_yaml(selected)


def plan_revision(plan_data: dict[str, object]) -> int | None:
    change_log = as_mapping(plan_data.get("change_log"))
    return parse_int(change_log.get("revision"))


def tasks(plan_data: dict[str, object]) -> list[dict[str, object]]:
    return [item for item in as_list(plan_data.get("tasks")) if isinstance(item, dict)]


def milestones(plan_data: dict[str, object]) -> list[dict[str, object]]:
    return [item for item in as_list(plan_data.get("milestones")) if isinstance(item, dict)]


def all_tasks_committed(plan_tasks: list[dict[str, object]]) -> bool:
    return bool(plan_tasks) and all(task.get("status") == "committed" for task in plan_tasks)


def next_task_id(plan_tasks: list[dict[str, object]], status_data: dict[str, object]) -> str | None:
    next_from_status = non_placeholder_string(status_data.get("next"))
    if next_from_status:
        for task in plan_tasks:
            if task.get("id") == next_from_status and task.get("status") != "committed":
                return next_from_status
    for task in plan_tasks:
        task_id = non_placeholder_string(task.get("id"))
        if task_id and task.get("status") != "committed":
            return task_id
    return None


def completed_audit_modules(audit_data: dict[str, object]) -> tuple[str | None, list[str]]:
    current: str | None = None
    completed: list[str] = []
    for item in as_list(audit_data.get("module_results")):
        module = as_mapping(item)
        if module.get("applicable") is not True:
            continue
        module_id = non_placeholder_string(module.get("module_id"))
        if module_id is None:
            continue
        smoke_required = module.get("smoke_required") is True
        smoke_status = str(module.get("smoke_status", "pending"))
        deep_status = str(module.get("deep_audit_status", "pending"))
        blocking = module.get("blocking") is True

        smoke_done = (not smoke_required) or smoke_status in DONE_SMOKE_STATUSES
        deep_done = deep_status in DONE_DEEP_STATUSES
        if smoke_done and deep_done and not blocking:
            completed.append(module_id)
            continue
        if current is None:
            current = module_id
    return current, completed


def task_lookup(plan_data: dict[str, object]) -> dict[str, dict[str, object]]:
    lookup: dict[str, dict[str, object]] = {}
    for task in tasks(plan_data):
        task_id = non_placeholder_string(task.get("id"))
        if task_id:
            lookup[task_id] = task
    return lookup


def milestone_lookup(plan_data: dict[str, object]) -> dict[str, dict[str, object]]:
    lookup: dict[str, dict[str, object]] = {}
    for milestone in milestones(plan_data):
        milestone_id = non_placeholder_string(milestone.get("id"))
        if milestone_id:
            lookup[milestone_id] = milestone
    return lookup


def milestone_owner_map(plan_data: dict[str, object]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for milestone in milestones(plan_data):
        milestone_id = non_placeholder_string(milestone.get("id"))
        if milestone_id is None:
            continue
        for task_id in as_string_list(milestone.get("tasks")):
            owners[task_id] = milestone_id
    return owners


def matches_scope(path_value: str, scope: str) -> bool:
    normalized_path = normalize_repo_path(path_value)
    normalized_scope = normalize_repo_path(scope)
    if not normalized_scope:
        return False
    if normalized_scope.endswith("/"):
        return normalized_path.startswith(normalized_scope)
    if any(char in normalized_scope for char in {"*", "?"}):
        return fnmatch(normalized_path, normalized_scope)
    return normalized_path == normalized_scope or normalized_path.startswith(normalized_scope + "/")


def task_matches_path(task: dict[str, object], path_value: str) -> bool:
    for scope in as_string_list(task.get("write_scope")) + as_string_list(task.get("read_scope")):
        if matches_scope(path_value, scope):
            return True
    return False


def allowed_write_scope_matches(task: dict[str, object], path_value: str) -> bool:
    for scope in as_string_list(task.get("write_scope")):
        if matches_scope(path_value, scope):
            return True
    return False


def tracked_repo_changes() -> list[str]:
    code, _ = git_output("rev-parse", "--git-dir")
    if code != 0:
        return []
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all", "--", *TRACKED_CHANGE_TARGETS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    changes: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path_text = line[3:].strip()
        if "->" in path_text:
            path_text = path_text.split("->", 1)[1].strip()
        if not path_text or path_text.startswith("harnass-os/"):
            continue
        changes.append(normalize_repo_path(path_text))
    return sorted(set(changes))


def unplanned_changes(plan_tasks: list[dict[str, object]], changes: list[str]) -> tuple[list[str], list[str]]:
    if not plan_tasks:
        return changes, []
    active_tasks = [task for task in plan_tasks if task.get("status") != "committed"]
    affected: list[str] = []
    unplanned: list[str] = []
    for path_value in changes:
        if any(allowed_write_scope_matches(task, path_value) for task in active_tasks):
            continue
        unplanned.append(path_value)
        for task in active_tasks:
            task_id = non_placeholder_string(task.get("id"))
            if task_id and task_matches_path(task, path_value) and task_id not in affected:
                affected.append(task_id)
    return unplanned, affected


def request_queue(data: dict[str, object]) -> list[dict[str, object]]:
    return [item for item in as_list(data.get("requests")) if isinstance(item, dict)]


def request_targets_active_plan(request: dict[str, object], active_plan_id: str | None) -> bool:
    target_plan_id = non_placeholder_string(request.get("target_plan_id"))
    if target_plan_id and active_plan_id and target_plan_id != active_plan_id:
        return False
    return True


def follow_up_mode(request: dict[str, object]) -> str | None:
    mode = non_placeholder_string(request.get("mode"))
    if mode in {"continue_current_milestone", "new_task", "modify", "scope_extend"}:
        return mode
    if mode in {"new_feature", "extend_scope"}:
        return "scope_extend"
    return None


def replan_change_type(request: dict[str, object]) -> str | None:
    change_type = non_placeholder_string(request.get("change_type"))
    if change_type in {
        "tech_stack_restructure",
        "architecture_rework",
        "major_feature_removal",
        "major_feature_redo",
        "platform_shift",
        "ambiguous",
    }:
        return change_type
    if change_type in {"feature_delete_redo", "major_redo"}:
        return "major_feature_redo"
    return None


def request_routing_decision(request: dict[str, object], *, queue_type: str) -> str | None:
    routing = non_placeholder_string(request.get("routing_decision"))
    if routing in {"follow_up", "re_plan", "needs_human_triage"}:
        return routing
    if queue_type == "follow_up":
        if follow_up_mode(request):
            return "follow_up"
        if non_placeholder_string(request.get("mode")) == "revamp":
            return "needs_human_triage"
        return None
    change_type = replan_change_type(request)
    if change_type == "ambiguous":
        return "needs_human_triage"
    if change_type:
        return "re_plan"
    return None


def pending_user_requests(data: dict[str, object], active_plan_id: str | None) -> list[dict[str, object]]:
    pending: list[dict[str, object]] = []
    for request in request_queue(data):
        if request.get("source") != "user":
            continue
        if request.get("status") != "pending":
            continue
        if request.get("auto_approve") is not True:
            continue
        if request_routing_decision(request, queue_type="follow_up") != "follow_up":
            continue
        if not request_targets_active_plan(request, active_plan_id):
            continue
        pending.append(request)
    return pending


def pending_replan_requests(data: dict[str, object], active_plan_id: str | None) -> list[dict[str, object]]:
    pending: list[dict[str, object]] = []
    for request in request_queue(data):
        if request.get("source") != "user":
            continue
        if request.get("status") != "pending":
            continue
        if request_routing_decision(request, queue_type="re_plan") != "re_plan":
            continue
        if not request_targets_active_plan(request, active_plan_id):
            continue
        pending.append(request)
    return pending


def approved_replan_requests(data: dict[str, object], active_plan_id: str | None) -> list[dict[str, object]]:
    return [
        request
        for request in pending_replan_requests(data, active_plan_id)
        if non_placeholder_string(request.get("approval_status")) == "approved"
    ]


def routed_replan_requests(data: dict[str, object], active_plan_id: str | None) -> list[dict[str, object]]:
    routed: list[dict[str, object]] = []
    for request in request_queue(data):
        if request.get("source") != "user":
            continue
        if request.get("status") != "routed":
            continue
        if request_routing_decision(request, queue_type="re_plan") != "re_plan":
            continue
        if not request_targets_active_plan(request, active_plan_id):
            continue
        routed.append(request)
    return routed


def pending_triage_requests(data: dict[str, object], active_plan_id: str | None) -> list[dict[str, object]]:
    pending: list[dict[str, object]] = []
    for request in request_queue(data):
        if request.get("source") != "user":
            continue
        if request.get("status") not in {"pending", "triage_required"}:
            continue
        if request_routing_decision(request, queue_type="re_plan") != "needs_human_triage":
            continue
        if not request_targets_active_plan(request, active_plan_id):
            continue
        pending.append(request)
    return pending


def run_guard(command: str) -> tuple[bool, str]:
    if not GUARD_FILE.is_file():
        return False, f"missing guard entry: {GUARD_FILE}"
    result = subprocess.run(
        [sys.executable, str(GUARD_FILE), command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    message = (result.stdout + result.stderr).strip()
    return result.returncode == 0, message


def inspect_repo_state(previous: dict[str, object]) -> dict[str, object]:
    status_data = read_optional_yaml(STATUS_FILE)
    run_data = read_optional_yaml(RUN_LEDGER_FILE)
    deploy_data = read_optional_yaml(DEPLOY_FILE)
    release_data = read_optional_yaml(RELEASE_FILE)
    audit_data = read_optional_yaml(AUDIT_FILE)
    request_data = read_optional_yaml(CHANGE_REQUEST_FILE)
    replan_data = read_optional_yaml(REPLAN_REQUEST_FILE)
    plan_path, plan_data = select_plan()
    plan_tasks = tasks(plan_data)
    tracked_changes = tracked_repo_changes()
    drift_changes, affected_task_ids = (
        unplanned_changes(plan_tasks, tracked_changes) if plan_data else (tracked_changes, [])
    )
    current_module, completed_modules = completed_audit_modules(audit_data)
    active_plan_id = non_placeholder_string(plan_data.get("id"))
    pending_requests = pending_user_requests(request_data, active_plan_id)
    pending_replans = pending_replan_requests(replan_data, active_plan_id)
    approved_replans = approved_replan_requests(replan_data, active_plan_id)
    routed_replans = routed_replan_requests(replan_data, active_plan_id)
    pending_triage = pending_triage_requests(replan_data, active_plan_id)
    pending_request_ids = [
        non_placeholder_string(request.get("request_id")) or f"request-{index + 1}"
        for index, request in enumerate(pending_requests)
    ]
    pending_replan_request_ids = [
        non_placeholder_string(request.get("request_id")) or f"replan-{index + 1}"
        for index, request in enumerate(pending_replans)
    ]
    approved_replan_request_ids = [
        non_placeholder_string(request.get("request_id")) or f"replan-approved-{index + 1}"
        for index, request in enumerate(approved_replans)
    ]
    routed_replan_request_ids = [
        non_placeholder_string(request.get("request_id")) or f"replan-routed-{index + 1}"
        for index, request in enumerate(routed_replans)
    ]
    pending_triage_request_ids = [
        non_placeholder_string(request.get("request_id")) or f"triage-{index + 1}"
        for index, request in enumerate(pending_triage)
    ]

    orchestration = as_mapping(plan_data.get("orchestration"))
    sync_status = non_placeholder_string(orchestration.get("sync_status")) or "clean"
    if sync_status not in SYNC_STATUSES:
        sync_status = "clean"

    pending_events: list[str] = []
    observed_changes = drift_changes if plan_data else tracked_changes
    if tracked_changes and not plan_data:
        pending_events.append("planning_requested")
    if drift_changes and plan_data:
        pending_events.append("content_changed")
    if pending_request_ids:
        pending_events.append("user_change_request")
    if pending_replan_request_ids:
        pending_events.append("re_plan_requested")
    if pending_triage_request_ids:
        pending_events.append("manual_triage_required")
    if plan_path is not None and plan_data.get("status") != "approved":
        pending_events.extend(["planning_requested", "draft_written"])
    if plan_path is not None and plan_data.get("status") == "approved":
        pending_events.append("plan_approved")
    if all_tasks_committed(plan_tasks):
        pending_events.append("all_tasks_committed")
    if str(deploy_data.get("status", "draft")) in {"deployed", "rollback_required"}:
        pending_events.append("production_deployed")
    if str(audit_data.get("status", "pending")) == "passed":
        pending_events.append("all_audit_modules_passed")

    return {
        "bootstrap_ready": bootstrap_ready(),
        "bootstrap_history_exists": bootstrap_history_exists(),
        "status_data": status_data,
        "run_data": run_data,
        "deploy_data": deploy_data,
        "release_data": release_data,
        "audit_data": audit_data,
        "request_data": request_data,
        "replan_data": replan_data,
        "pending_user_requests": pending_requests,
        "pending_request_ids": pending_request_ids,
        "pending_replan_requests": pending_replans,
        "approved_replan_requests": approved_replans,
        "routed_replan_requests": routed_replans,
        "pending_triage_requests": pending_triage,
        "pending_replan_request_ids": pending_replan_request_ids,
        "approved_replan_request_ids": approved_replan_request_ids,
        "routed_replan_request_ids": routed_replan_request_ids,
        "pending_triage_request_ids": pending_triage_request_ids,
        "plan_path": plan_path,
        "plan_data": plan_data,
        "plan_tasks": plan_tasks,
        "tracked_changes": tracked_changes,
        "observed_changes": observed_changes,
        "affected_task_ids": affected_task_ids,
        "pending_events": sorted(set(pending_events)),
        "current_task_id": next_task_id(plan_tasks, status_data),
        "current_audit_module": current_module,
        "completed_audit_modules": completed_modules,
        "active_plan_id": active_plan_id,
        "active_plan_revision": plan_revision(plan_data),
        "release_affecting": plan_data.get("release_affecting") is True,
        "sync_status": sync_status,
    }


def ensure_request_id(request: dict[str, object], fallback_index: int) -> str:
    request_id = non_placeholder_string(request.get("request_id"))
    if request_id:
        return request_id
    seed = non_placeholder_string(request.get("summary")) or f"request-{fallback_index}"
    request_id = slugify(seed)
    request["request_id"] = request_id
    return request_id


def next_unique_identifier(existing: set[str], base: str) -> str:
    candidate = slugify(base)
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    index = 2
    while True:
        candidate = f"{slugify(base)}-{index}"
        if candidate not in existing:
            existing.add(candidate)
            return candidate
        index += 1


def milestone_complete(milestone: dict[str, object], task_index: dict[str, dict[str, object]]) -> bool:
    task_ids = as_string_list(milestone.get("tasks"))
    return bool(task_ids) and all(
        as_mapping(task_index.get(task_id)).get("status") == "committed" for task_id in task_ids
    )


def completed_milestone_ids(plan_data: dict[str, object]) -> list[str]:
    task_index = task_lookup(plan_data)
    completed: list[str] = []
    for milestone in milestones(plan_data):
        milestone_id = non_placeholder_string(milestone.get("id"))
        if milestone_id and milestone_complete(milestone, task_index):
            completed.append(milestone_id)
    return completed


def milestone_for_task(plan_data: dict[str, object], task_id: str | None) -> str | None:
    if task_id is None:
        return None
    return milestone_owner_map(plan_data).get(task_id)


def current_milestone_id(plan_data: dict[str, object], next_task: str | None) -> str | None:
    owner = milestone_for_task(plan_data, next_task)
    if owner:
        return owner
    task_index = task_lookup(plan_data)
    for milestone in milestones(plan_data):
        milestone_id = non_placeholder_string(milestone.get("id"))
        if milestone_id and not milestone_complete(milestone, task_index):
            return milestone_id
    return None


def preferred_validation_profile(plan_data: dict[str, object]) -> str:
    for task in tasks(plan_data):
        profile = non_placeholder_string(task.get("validation_profile"))
        if profile:
            return profile
    profiles = as_string_list(as_mapping(plan_data.get("global_validation")).get("profiles"))
    if profiles:
        return profiles[0]
    return "backend-contract"


def preferred_validation_commands(plan_data: dict[str, object]) -> list[str]:
    for task in tasks(plan_data):
        commands = as_string_list(task.get("validation_commands"))
        if commands:
            return commands
    return ["${test_command}", "${lint_command}", "${typecheck_command}"]


def derived_read_scope(write_scope: list[str]) -> list[str]:
    scopes: list[str] = []
    for path_value in write_scope:
        normalized = normalize_repo_path(path_value)
        if normalized.endswith("/"):
            scopes.append(normalized)
        elif "/" in normalized:
            scopes.append(normalized.rsplit("/", 1)[0] + "/")
        else:
            scopes.append(normalized)
    return scopes or ["src/"]


def derived_entrypoints(read_scope: list[str]) -> list[dict[str, str]]:
    scopes = read_scope or ["src/"]
    return [
        {
            "file": scope,
            "reason": "inspect current implementation before editing",
        }
        for scope in scopes[:2]
    ]


def normalized_entrypoints(value: object) -> list[dict[str, str]]:
    entries = [item for item in as_list(value) if isinstance(item, dict)]
    normalized: list[dict[str, str]] = []
    for item in entries:
        file_ref = non_placeholder_string(item.get("file"))
        reason = non_placeholder_string(item.get("reason")) or "inspect current implementation before editing"
        if file_ref:
            normalized.append({"file": file_ref, "reason": reason})
    return normalized


def execution_ready_projection(plan_data: dict[str, object], value: bool) -> dict[str, object]:
    existing = as_mapping(plan_data.get("execution_ready"))
    projected: dict[str, object] = {}
    for field in STANDARD_EXECUTION_READY_FIELDS:
        projected[field] = value
    for field in existing:
        projected[field] = value
    return projected


def append_change_log_entry(plan_data: dict[str, object], revision: int, message: str) -> None:
    change_log = ensure_mapping(plan_data, "change_log")
    entries = ensure_list(change_log, "entries")
    entries.append(f"r{revision}: {message}")
    change_log["revision"] = revision


def update_plan_orchestration(
    plan_data: dict[str, object],
    *,
    sync_status: str,
    observed_changes: list[str],
    affected_task_ids: list[str],
    last_change_request_ids: list[str],
    last_replan_request_ids: list[str] | None = None,
    routing_decision: str | None = None,
    manual_approval_required: bool | None = None,
    timestamp: str,
) -> None:
    orchestration = ensure_mapping(plan_data, "orchestration")
    orchestration["sync_status"] = sync_status
    orchestration["observed_changes"] = observed_changes
    orchestration["affected_task_ids"] = affected_task_ids
    orchestration["last_auto_update_at"] = timestamp
    orchestration["last_change_request_ids"] = last_change_request_ids
    orchestration["last_replan_request_ids"] = [] if last_replan_request_ids is None else last_replan_request_ids
    orchestration["routing_decision"] = routing_decision or "none"
    orchestration["manual_approval_required"] = bool(manual_approval_required)


def build_follow_up_tasks(
    plan_data: dict[str, object],
    requests: list[dict[str, object]],
    revision: int,
) -> tuple[list[dict[str, object]], dict[str, list[str]]]:
    existing_task_ids = set(task_lookup(plan_data))
    task_counter = len(tasks(plan_data))
    validation_profile = preferred_validation_profile(plan_data)
    validation_commands = preferred_validation_commands(plan_data)
    new_tasks: list[dict[str, object]] = []
    request_task_map: dict[str, list[str]] = {}

    for request_index, request in enumerate(requests, 1):
        request_id = ensure_request_id(request, request_index)
        blueprints = [item for item in as_list(request.get("tasks")) if isinstance(item, dict)] or [request]
        request_task_map[request_id] = []
        for blueprint_object in blueprints:
            blueprint = as_mapping(blueprint_object)
            task_counter += 1
            task_id = next_unique_identifier(existing_task_ids, f"t{task_counter}-{request_id}")
            goal = (
                non_placeholder_string(blueprint.get("goal"))
                or non_placeholder_string(request.get("summary"))
                or f"Follow up on {request_id}"
            )
            write_scope = (
                as_string_list(blueprint.get("write_scope"))
                or as_string_list(request.get("write_scope"))
                or [f"src/{slugify(request_id)}.py"]
            )
            read_scope = (
                as_string_list(blueprint.get("read_scope"))
                or as_string_list(request.get("read_scope"))
                or derived_read_scope(write_scope)
            )
            entrypoints = (
                normalized_entrypoints(blueprint.get("entrypoints"))
                or normalized_entrypoints(request.get("entrypoints"))
                or derived_entrypoints(read_scope)
            )
            task_validation_commands = (
                as_string_list(blueprint.get("validation_commands"))
                or as_string_list(request.get("validation_commands"))
                or validation_commands
            )
            artifacts_updated = as_string_list(blueprint.get("artifacts_updated")) or write_scope
            new_task = {
                "id": task_id,
                "goal": goal,
                "depends_on": as_string_list(blueprint.get("depends_on")),
                "read_scope": read_scope,
                "write_scope": write_scope,
                "entrypoints": entrypoints,
                "agent_role": non_placeholder_string(blueprint.get("agent_role")) or "solo",
                "worktree_required": blueprint.get("worktree_required") is True,
                "implementation_strategy": non_placeholder_string(blueprint.get("implementation_strategy"))
                or "rewrite-by-replacement",
                "implementation_steps": [
                    {
                        "step": f"Implement {goal}",
                        "action": non_placeholder_string(blueprint.get("action")) or "modify",
                        "tool": non_placeholder_string(blueprint.get("tool")) or "Write",
                        "output": write_scope[0],
                    }
                ],
                "rewrite_policy": non_placeholder_string(blueprint.get("rewrite_policy")) or "replacement-first",
                "validation_profile": non_placeholder_string(blueprint.get("validation_profile")) or validation_profile,
                "validation_commands": task_validation_commands,
                "artifacts_updated": artifacts_updated,
                "done_definition": non_placeholder_string(blueprint.get("done_definition")) or goal,
                "commit_required": blueprint.get("commit_required") is not False,
                "handoff_output": non_placeholder_string(blueprint.get("handoff_output"))
                or f"harnass-os/documents/handoffs/{task_id}.yaml",
                "status": "pending",
                "introduced_in_revision": revision,
            }
            new_tasks.append(new_task)
            request_task_map[request_id].append(task_id)
    return new_tasks, request_task_map


def build_follow_up_milestone(
    plan_data: dict[str, object], revision: int, task_ids: list[str], requests: list[dict[str, object]]
) -> dict[str, object]:
    existing_milestone_ids = set(milestone_lookup(plan_data))
    milestone_number = len(milestones(plan_data)) + 1
    milestone_id = next_unique_identifier(existing_milestone_ids, f"m{milestone_number}-follow-up-r{revision}")
    summary = " + ".join(filter(None, [non_placeholder_string(request.get("summary")) for request in requests]))
    summary = summary or f"Deliver follow-up revision {revision}"
    previous_milestones = milestones(plan_data)
    depends_on = []
    if previous_milestones:
        previous_id = non_placeholder_string(previous_milestones[-1].get("id"))
        if previous_id:
            depends_on = [previous_id]
    return {
        "id": milestone_id,
        "capability": f"follow-up-r{revision}",
        "goal": f"Deliver follow-up changes: {summary}",
        "depends_on": depends_on,
        "parallel_policy": "sequential",
        "acceptance_criteria": [summary],
        "validation_commands": preferred_validation_commands(plan_data),
        "done_when": f"follow-up tasks {', '.join(task_ids)} are committed",
        "failure_policy": "block-next",
        "demo_flow": summary,
        "exit_validation": preferred_validation_profile(plan_data),
        "tasks": task_ids,
        "status": "pending",
        "source": "follow_up",
        "introduced_in_revision": revision,
    }


def status_projection(plan_data: dict[str, object], existing_status: dict[str, object]) -> dict[str, object]:
    plan_tasks = tasks(plan_data)
    next_task = next_task_id(plan_tasks, existing_status)
    completed_task_ids = [
        task_id for task_id, task in task_lookup(plan_data).items() if task.get("status") == "committed"
    ]
    return {
        "plan_id": non_placeholder_string(plan_data.get("id")) or "<fill>",
        "plan_revision": plan_revision(plan_data) or 0,
        "active_run": existing_status.get("active_run", "<fill>"),
        "current_milestone": current_milestone_id(plan_data, next_task) or "<fill>",
        "completed": completed_task_ids,
        "next": next_task or "<fill>",
        "known_issues": as_string_list(existing_status.get("known_issues")),
        "follow_ups": as_string_list(existing_status.get("follow_ups")),
        "decision_notes": as_string_list(existing_status.get("decision_notes")),
        "deployment_notes": as_string_list(existing_status.get("deployment_notes")),
    }


def status_icon(task_status: str) -> str:
    if task_status == "committed":
        return "[x]"
    if task_status in {"in_progress", "ready", "validated"}:
        return "[~]"
    if task_status in {"blocked", "failed"}:
        return "[!]"
    return "[ ]"


def markdown_cell(value: object) -> str:
    text = str(value).replace("\n", " ").strip()
    return text.replace("|", "\\|") if text else "-"


def render_tracker(plan_data: dict[str, object], existing_text: str | None, timestamp: str) -> str:
    generated_at = timestamp
    if existing_text:
        match = re.search(r"^- generated_at:\s*(.+)$", existing_text, flags=re.MULTILINE)
        if match:
            generated_at = match.group(1).strip()
    task_index = task_lookup(plan_data)
    lines = [
        "# Milestone Tasks",
        "",
        f"- plan_id: {non_placeholder_string(plan_data.get('id')) or '<fill>'}",
        f"- plan_status: {plan_data.get('status', 'draft')}",
        f"- plan_revision: {plan_revision(plan_data) or 0}",
        f"- task_horizon: {non_placeholder_string(plan_data.get('task_horizon')) or '<fill>'}",
        f"- generated_at: {generated_at}",
        f"- last_updated: {timestamp}",
        "",
    ]
    for milestone in milestones(plan_data):
        milestone_id = non_placeholder_string(milestone.get("id")) or "milestone"
        heading = "[x]" if milestone_complete(milestone, task_index) else "[ ]"
        goal = non_placeholder_string(milestone.get("goal")) or "Untitled milestone"
        lines.extend(
            [
                f"## {heading} {milestone_id} - {goal}",
                "",
                "| Status | Task | Goal | Depends On | Validation |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for task_id in as_string_list(milestone.get("tasks")):
            task = as_mapping(task_index.get(task_id))
            lines.append(
                "| {status} | {task_id} | {goal} | {depends_on} | {validation} |".format(
                    status=status_icon(str(task.get("status", "pending"))),
                    task_id=markdown_cell(task_id),
                    goal=markdown_cell(non_placeholder_string(task.get("goal")) or "Untitled task"),
                    depends_on=markdown_cell(", ".join(as_string_list(task.get("depends_on"))) or "—"),
                    validation=markdown_cell(
                        non_placeholder_string(task.get("validation_profile"))
                        or ", ".join(as_string_list(task.get("validation_commands")))
                        or "—"
                    ),
                )
            )
        lines.append("")
    lines.extend(["---", "Generated by harnass-engineer-plan. Updated by harnass-engineer orchestrator."])
    return "\n".join(lines).rstrip() + "\n"


def sync_projection_documents(context: dict[str, object]) -> list[Path]:
    plan_path = context["plan_path"]
    if plan_path is None:
        return []
    changed_files: list[Path] = []
    if write_yaml(STATUS_FILE, status_projection(as_mapping(context["plan_data"]), as_mapping(context["status_data"]))):
        changed_files.append(STATUS_FILE)
    tracker_text = render_tracker(
        as_mapping(context["plan_data"]),
        TRACKER_FILE.read_text(encoding="utf-8") if TRACKER_FILE.is_file() else None,
        now_timestamp(),
    )
    if write_text(TRACKER_FILE, tracker_text):
        changed_files.append(TRACKER_FILE)
    return changed_files


def finalize_replan_requests(context: dict[str, object]) -> SyncResult:
    plan_path = context["plan_path"]
    if plan_path is None or context["plan_data"].get("status") != "approved":
        return SyncResult([], "none", None, None)
    if context["pending_replan_request_ids"] or context["pending_triage_request_ids"]:
        return SyncResult([], "none", None, None)

    orchestration = as_mapping(context["plan_data"].get("orchestration"))
    routed_request_ids = context["routed_replan_request_ids"]
    if not routed_request_ids and not (
        non_placeholder_string(orchestration.get("routing_decision")) in {"re_plan", "needs_human_triage"}
        or orchestration.get("manual_approval_required") is True
    ):
        return SyncResult([], "none", None, None)

    timestamp = now_timestamp()
    plan_data = deepcopy(as_mapping(context["plan_data"]))
    replan_data = deepcopy(as_mapping(context["replan_data"]))
    status_data = deepcopy(as_mapping(context["status_data"]))
    revision = plan_revision(plan_data) or 0
    request_ids = routed_request_ids or as_string_list(
        as_mapping(plan_data.get("orchestration")).get("last_replan_request_ids")
    )
    update_plan_orchestration(
        plan_data,
        sync_status="clean",
        observed_changes=[],
        affected_task_ids=[],
        last_change_request_ids=as_string_list(
            as_mapping(plan_data.get("orchestration")).get("last_change_request_ids")
        ),
        last_replan_request_ids=request_ids,
        routing_decision="none",
        manual_approval_required=False,
        timestamp=timestamp,
    )

    queue = request_queue(replan_data)
    for index, request in enumerate(queue, 1):
        request_id = ensure_request_id(request, index)
        if request_id not in request_ids or request.get("status") != "routed":
            continue
        request["status"] = "fulfilled"
        request["fulfilled_at"] = timestamp
        request["fulfilled_revision"] = revision

    changed_files: list[Path] = []
    if write_yaml(plan_path, plan_data):
        changed_files.append(plan_path)
    if write_yaml(REPLAN_REQUEST_FILE, replan_data):
        changed_files.append(REPLAN_REQUEST_FILE)
    if write_yaml(STATUS_FILE, status_projection(plan_data, status_data)):
        changed_files.append(STATUS_FILE)
    return SyncResult(changed_files, "re_plan_request", "re-plan approved and execution unblocked", timestamp)


def apply_replan_requests(context: dict[str, object]) -> SyncResult:
    plan_path = context["plan_path"]
    if (
        plan_path is None
        or context["plan_data"].get("status") != "approved"
        or not context["approved_replan_requests"]
        or context["pending_triage_request_ids"]
    ):
        return SyncResult([], "none", None, None)

    timestamp = now_timestamp()
    plan_data = deepcopy(as_mapping(context["plan_data"]))
    replan_data = deepcopy(as_mapping(context["replan_data"]))
    status_data = deepcopy(as_mapping(context["status_data"]))
    revision = (plan_revision(plan_data) or 0) + 1
    queue = request_queue(replan_data)
    approved_requests = approved_replan_requests(replan_data, non_placeholder_string(plan_data.get("id")))
    request_ids = [ensure_request_id(request, index + 1) for index, request in enumerate(approved_requests)]
    affected_surfaces: list[str] = []
    for request in approved_requests:
        for surface in as_string_list(request.get("affected_surfaces")):
            if surface not in affected_surfaces:
                affected_surfaces.append(surface)

    plan_data["status"] = "draft"
    review = ensure_mapping(plan_data, "review")
    review["state"] = "needs_reapproval"
    review["approved_for_execution"] = False
    if "blocking_findings" not in review:
        review["blocking_findings"] = []
    plan_data["execution_ready"] = execution_ready_projection(plan_data, False)
    update_plan_orchestration(
        plan_data,
        sync_status="needs_replan",
        observed_changes=affected_surfaces,
        affected_task_ids=[],
        last_change_request_ids=as_string_list(
            as_mapping(plan_data.get("orchestration")).get("last_change_request_ids")
        ),
        last_replan_request_ids=request_ids,
        routing_decision="re_plan",
        manual_approval_required=True,
        timestamp=timestamp,
    )
    append_change_log_entry(
        plan_data, revision, f"structural change requests {', '.join(request_ids)} routed into a full re-plan"
    )

    for index, request in enumerate(queue, 1):
        request_id = ensure_request_id(request, index)
        if request_id not in request_ids:
            continue
        request["status"] = "routed"
        request["routed_at"] = timestamp
        request["routed_revision"] = revision
        request["replacement_plan_id"] = non_placeholder_string(plan_data.get("id")) or request.get(
            "replacement_plan_id"
        )

    changed_files: list[Path] = []
    if write_yaml(plan_path, plan_data):
        changed_files.append(plan_path)
    if write_yaml(REPLAN_REQUEST_FILE, replan_data):
        changed_files.append(REPLAN_REQUEST_FILE)
    if write_yaml(STATUS_FILE, status_projection(plan_data, status_data)):
        changed_files.append(STATUS_FILE)
    return SyncResult(changed_files, "re_plan_request", "structural change request routed into full re-plan", timestamp)


def apply_user_change_requests(context: dict[str, object]) -> SyncResult:
    plan_path = context["plan_path"]
    if (
        plan_path is None
        or not context["pending_user_requests"]
        or context["pending_replan_request_ids"]
        or context["pending_triage_request_ids"]
    ):
        return SyncResult([], "none", None, None)

    timestamp = now_timestamp()
    plan_data = deepcopy(as_mapping(context["plan_data"]))
    request_data = deepcopy(as_mapping(context["request_data"]))
    status_data = deepcopy(as_mapping(context["status_data"]))
    revision = (plan_revision(plan_data) or 0) + 1
    queue = request_queue(request_data)
    pending_requests = pending_user_requests(request_data, non_placeholder_string(plan_data.get("id")))
    new_tasks, request_task_map = build_follow_up_tasks(plan_data, pending_requests, revision)
    new_task_ids = [str(task["id"]) for task in new_tasks]
    follow_up_milestone = build_follow_up_milestone(plan_data, revision, new_task_ids, pending_requests)

    plan_data["tasks"] = tasks(plan_data) + new_tasks
    plan_data["milestones"] = milestones(plan_data) + [follow_up_milestone]
    plan_data["status"] = "approved"
    review = ensure_mapping(plan_data, "review")
    review["state"] = "completed"
    review["approved_for_execution"] = True
    if "blocking_findings" not in review:
        review["blocking_findings"] = []
    plan_data["execution_ready"] = execution_ready_projection(plan_data, True)
    request_ids = [ensure_request_id(request, index + 1) for index, request in enumerate(pending_requests)]
    update_plan_orchestration(
        plan_data,
        sync_status="clean",
        observed_changes=[],
        affected_task_ids=new_task_ids,
        last_change_request_ids=request_ids,
        last_replan_request_ids=as_string_list(
            as_mapping(plan_data.get("orchestration")).get("last_replan_request_ids")
        ),
        routing_decision="follow_up",
        manual_approval_required=False,
        timestamp=timestamp,
    )
    append_change_log_entry(
        plan_data, revision, f"auto-approved follow-up milestone from requests {', '.join(request_ids)}"
    )

    for index, request in enumerate(queue, 1):
        request_id = ensure_request_id(request, index)
        if request_id not in request_task_map:
            continue
        request["status"] = "applied"
        request["applied_at"] = timestamp
        request["applied_revision"] = revision
        request["applied_in_revision"] = revision
        request["applied_milestone_id"] = follow_up_milestone["id"]
        request["applied_task_ids"] = request_task_map[request_id]

    changed_files: list[Path] = []
    if write_yaml(plan_path, plan_data):
        changed_files.append(plan_path)
    if write_yaml(CHANGE_REQUEST_FILE, request_data):
        changed_files.append(CHANGE_REQUEST_FILE)
    if write_yaml(STATUS_FILE, status_projection(plan_data, status_data)):
        changed_files.append(STATUS_FILE)
    return SyncResult(
        changed_files, "user_change_request", "follow-up milestone auto-approved from user change request", timestamp
    )


def apply_inferred_drift(context: dict[str, object]) -> SyncResult:
    plan_path = context["plan_path"]
    if (
        plan_path is None
        or context["plan_data"].get("status") != "approved"
        or not context["observed_changes"]
        or context["pending_replan_request_ids"]
        or context["pending_triage_request_ids"]
    ):
        return SyncResult([], "none", None, None)

    timestamp = now_timestamp()
    plan_data = deepcopy(as_mapping(context["plan_data"]))
    status_data = deepcopy(as_mapping(context["status_data"]))
    revision = (plan_revision(plan_data) or 0) + 1
    plan_data["status"] = "draft"
    review = ensure_mapping(plan_data, "review")
    review["state"] = "needs_reapproval"
    review["approved_for_execution"] = False
    if "blocking_findings" not in review:
        review["blocking_findings"] = []
    plan_data["execution_ready"] = execution_ready_projection(plan_data, False)
    update_plan_orchestration(
        plan_data,
        sync_status="needs_review",
        observed_changes=context["observed_changes"],
        affected_task_ids=context["affected_task_ids"],
        last_change_request_ids=[],
        last_replan_request_ids=[],
        routing_decision="none",
        manual_approval_required=False,
        timestamp=timestamp,
    )
    append_change_log_entry(
        plan_data, revision, f"auto-drafted after inferred drift in {', '.join(context['observed_changes'])}"
    )

    changed_files: list[Path] = []
    if write_yaml(plan_path, plan_data):
        changed_files.append(plan_path)
    if write_yaml(STATUS_FILE, status_projection(plan_data, status_data)):
        changed_files.append(STATUS_FILE)
    return SyncResult(changed_files, "inferred_drift", "plan auto-drafted after inferred drift", timestamp)


def resolve_sync_snapshot(
    previous: dict[str, object], context: dict[str, object], sync_result: SyncResult
) -> dict[str, object]:
    orchestration = as_mapping(context["plan_data"].get("orchestration"))
    last_request_ids = as_string_list(orchestration.get("last_change_request_ids"))
    last_replan_request_ids = as_string_list(orchestration.get("last_replan_request_ids"))
    routing_decision = non_placeholder_string(orchestration.get("routing_decision")) or "none"
    sync_lane = sync_result.lane
    sync_status = context["sync_status"]
    if (
        sync_lane == "re_plan_request"
        and sync_status == "clean"
        and routing_decision == "none"
        and not context["pending_replan_request_ids"]
        and not context["pending_triage_request_ids"]
    ):
        sync_lane = "none"
    if sync_lane == "none":
        if context["pending_triage_request_ids"]:
            sync_lane = "manual_triage"
            sync_status = "needs_human_triage"
        elif context["pending_replan_request_ids"]:
            sync_lane = "re_plan_request"
            sync_status = "needs_replan"
        elif context["pending_request_ids"]:
            sync_lane = "user_change_request"
            sync_status = "applying_followup"
        elif sync_status == "needs_human_triage" or routing_decision == "needs_human_triage":
            sync_lane = "manual_triage"
            sync_status = "needs_human_triage"
        elif sync_status == "needs_replan" or routing_decision == "re_plan":
            sync_lane = "re_plan_request"
            sync_status = "needs_replan"
        elif sync_status == "needs_review":
            sync_lane = "inferred_drift"
        elif last_request_ids and routing_decision == "follow_up":
            sync_lane = "user_change_request"
        elif last_replan_request_ids and routing_decision in {"re_plan", "needs_human_triage"}:
            sync_lane = "re_plan_request"
        else:
            sync_lane = "none"
            sync_status = "clean"
    last_plan_sync_at = (
        sync_result.last_plan_sync_at
        or non_placeholder_string(orchestration.get("last_auto_update_at"))
        or non_placeholder_string(previous.get("last_plan_sync_at"))
    )
    affected_task_ids = as_string_list(orchestration.get("affected_task_ids")) or context["affected_task_ids"]
    return {
        "sync_lane": sync_lane,
        "sync_status": sync_status,
        "affected_task_ids": affected_task_ids,
        "pending_change_request_ids": context["pending_request_ids"],
        "pending_replan_request_ids": context["pending_replan_request_ids"],
        "pending_triage_request_ids": context["pending_triage_request_ids"],
        "last_plan_sync_at": last_plan_sync_at,
    }


def determine_state(
    previous: dict[str, object], context: dict[str, object], sync_snapshot: dict[str, object]
) -> tuple[str, str | None]:
    if not context["bootstrap_ready"]:
        if context["bootstrap_history_exists"]:
            return "STARTING", None
        return "IDLE", None

    plan_data = as_mapping(context["plan_data"])
    plan_tasks = context["plan_tasks"]
    deploy_data = as_mapping(context["deploy_data"])
    release_data = as_mapping(context["release_data"])
    audit_data = as_mapping(context["audit_data"])

    if not plan_data:
        if context["tracked_changes"]:
            return "PLANNING", None
        return "READY_FOR_PLAN", None

    if sync_snapshot["sync_status"] == "needs_human_triage":
        return "PLAN_REVIEW", "change routing requires human triage before planning can continue"
    if sync_snapshot["sync_status"] == "needs_replan" and plan_data.get("status") == "approved":
        return "PLAN_REVIEW", "structural change requires re-plan approval before execution can continue"

    if plan_data.get("status") != "approved":
        review = as_mapping(plan_data.get("review"))
        if sync_snapshot["sync_status"] == "needs_replan":
            return "PLANNING", None
        if (
            sync_snapshot["sync_status"] == "needs_review"
            or review.get("approved_for_execution") is True
            or review.get("state") in {"completed", "needs_reapproval"}
        ):
            return "PLAN_REVIEW", None
        return "PLANNING", None

    execution_ok, execution_error = run_guard("check-execution-ready")
    if not execution_ok:
        return "BLOCKED", execution_error or "execution readiness failed"

    if not all_tasks_committed(plan_tasks):
        return "IMPLEMENTING", None

    if plan_data.get("release_affecting") is not True:
        return "COMPLETE", None

    deploy_status = str(deploy_data.get("status", "draft"))
    if deploy_status not in {"deployed", "rollback_required"}:
        if deploy_status != "draft":
            deploy_ok, deploy_error = run_guard("check-deployment-ready")
            if not deploy_ok:
                return "BLOCKED", deploy_error or "deployment readiness failed"
        return "DEPLOYING", None

    if deploy_data.get("post_deploy_audit_required") is not True:
        return "COMPLETE", None

    audit_status = str(audit_data.get("status", "pending"))
    release_status = str(release_data.get("status", "draft"))
    final_audit_status = str(release_data.get("final_audit_status", "pending"))
    if audit_status == "failed" or release_status == "audit_failed" or final_audit_status == "failed":
        if sync_snapshot["sync_status"] == "needs_replan":
            return "PLANNING", None
        if sync_snapshot["sync_status"] == "needs_human_triage":
            return "PLAN_REVIEW", "audit failed — change routing requires human triage"
        return "BLOCKED", "final audit failed and remediation is required"
    if audit_status == "passed" and release_status == "complete" and final_audit_status == "passed":
        return "COMPLETE", None

    audit_ready, audit_error = run_guard("check-final-audit-ready")
    if not audit_ready:
        return "BLOCKED", audit_error or "final audit readiness failed"
    return "FINAL_AUDITING", None


def build_state(previous: dict[str, object], context: dict[str, object], sync_result: SyncResult) -> dict[str, object]:
    sync_snapshot = resolve_sync_snapshot(previous, context, sync_result)
    next_state, error = determine_state(previous, context, sync_snapshot)
    previous_state = non_placeholder_string(previous.get("state")) or "IDLE"
    stable_state = (
        previous.get("previous_stable_state")
        if isinstance(previous.get("previous_stable_state"), str)
        else previous_state
    )
    if next_state != "BLOCKED":
        stable_state = next_state
    elif stable_state == "BLOCKED":
        stable_state = previous_state if previous_state != "BLOCKED" else "IDLE"

    transition_reason = "repo reality re-evaluated"
    if sync_result.transition_note:
        transition_reason = sync_result.transition_note
    elif sync_snapshot["sync_status"] == "needs_human_triage":
        transition_reason = "change routing awaits human triage"
    elif sync_snapshot["sync_status"] == "needs_replan" and context["plan_data"].get("status") == "approved":
        transition_reason = "structural change request awaits re-plan authorization"
    elif sync_snapshot["sync_status"] == "needs_replan":
        transition_reason = "structural change routed back into planning"
    elif context["observed_changes"]:
        transition_reason = "content change detected"
    elif next_state == "PLAN_REVIEW":
        transition_reason = "plan draft awaiting approval"
    elif next_state == "IMPLEMENTING":
        transition_reason = "approved plan ready for execution"
    elif next_state == "DEPLOYING":
        transition_reason = "release-affecting implementation completed"
    elif next_state == "FINAL_AUDITING":
        transition_reason = "production deploy recorded and final audit pending"
    elif next_state == "COMPLETE":
        transition_reason = "lifecycle closeout conditions satisfied"
    elif next_state == "BLOCKED" and error:
        transition_reason = "blocking guard or audit failure detected"
    elif next_state == "READY_FOR_PLAN":
        transition_reason = "bootstrap ready and no active plan found"
    elif next_state == "PLANNING":
        transition_reason = "planning input detected"
    elif next_state == "STARTING":
        transition_reason = "bootstrap history detected before scaffold completion"

    return {
        "state": next_state,
        "previous_stable_state": stable_state,
        "active_plan_id": context["active_plan_id"],
        "active_plan_revision": context["active_plan_revision"],
        "release_affecting": context["release_affecting"],
        "current_task_id": context["current_task_id"] if next_state == "IMPLEMENTING" else None,
        "current_audit_module": context["current_audit_module"] if next_state == "FINAL_AUDITING" else None,
        "completed_audit_modules": context["completed_audit_modules"]
        if next_state in {"FINAL_AUDITING", "COMPLETE"}
        else [],
        "pending_events": context["pending_events"],
        "observed_changes": context["observed_changes"],
        "sync_lane": sync_snapshot["sync_lane"],
        "sync_status": sync_snapshot["sync_status"],
        "affected_task_ids": sync_snapshot["affected_task_ids"],
        "pending_change_request_ids": sync_snapshot["pending_change_request_ids"],
        "pending_replan_request_ids": sync_snapshot["pending_replan_request_ids"],
        "pending_triage_request_ids": sync_snapshot["pending_triage_request_ids"],
        "last_plan_sync_at": sync_snapshot["last_plan_sync_at"],
        "last_transition": f"{previous_state} -> {next_state} ({transition_reason})",
        "last_error": error,
        "updated_at": now_timestamp(),
    }


def print_summary(state: dict[str, object]) -> None:
    parts = [f"state={state['state']}"]
    plan_id = non_placeholder_string(state.get("active_plan_id"))
    if plan_id:
        parts.append(f"plan={plan_id}")
    task_id = non_placeholder_string(state.get("current_task_id"))
    if task_id:
        parts.append(f"task={task_id}")
    module_id = non_placeholder_string(state.get("current_audit_module"))
    if module_id:
        parts.append(f"audit_module={module_id}")
    sync_lane = non_placeholder_string(state.get("sync_lane"))
    if sync_lane and sync_lane != "none":
        parts.append(f"sync={sync_lane}:{state.get('sync_status')}")
    error = non_placeholder_string(state.get("last_error"))
    if error:
        parts.append(f"error={error}")
    print(" ".join(parts))


def command_sync_tracker() -> int:
    previous = load_orchestrator_state()
    context = inspect_repo_state(previous)
    projection_changes = sync_projection_documents(context)
    if projection_changes:
        stage_files(projection_changes)
    return 0


def command_tick(stage: bool) -> int:
    previous = load_orchestrator_state()
    context = inspect_repo_state(previous)
    changed_files: list[Path] = []
    sync_result = SyncResult([], "none", None, None)

    finalize_result = finalize_replan_requests(context)
    if finalize_result.changed_files:
        changed_files.extend(finalize_result.changed_files)
        sync_result = finalize_result
        context = inspect_repo_state(previous)

    replan_result = apply_replan_requests(context)
    if replan_result.changed_files:
        changed_files.extend(replan_result.changed_files)
        sync_result = replan_result
        context = inspect_repo_state(previous)

    request_result = apply_user_change_requests(context)
    if request_result.changed_files:
        changed_files.extend(request_result.changed_files)
        sync_result = request_result
        context = inspect_repo_state(previous)

    drift_result = apply_inferred_drift(context)
    if drift_result.changed_files:
        changed_files.extend(drift_result.changed_files)
        sync_result = drift_result
        context = inspect_repo_state(previous)

    projection_changes = sync_projection_documents(context)
    if projection_changes:
        changed_files.extend(projection_changes)
        context = inspect_repo_state(previous)

    state = build_state(previous, context, sync_result)
    if write_yaml(ORCHESTRATOR_FILE, state):
        changed_files.append(ORCHESTRATOR_FILE)
    if stage and changed_files:
        stage_files(changed_files)
    print_summary(state)
    return 0


def command_show() -> int:
    print(dump_yaml(load_orchestrator_state()))
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal harness lifecycle orchestrator.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tick = subparsers.add_parser("tick", help="Recompute lifecycle state from repo documents.")
    tick.add_argument(
        "--stage", action="store_true", help="Stage orchestrator/current.yaml and synced docs if they change."
    )

    subparsers.add_parser("show", help="Print the current orchestrator state.")
    subparsers.add_parser("sync-tracker", help="Sync milestone-tasks.md and status projection.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv[1:])
        if args.command == "tick":
            return command_tick(stage=bool(args.stage))
        if args.command == "show":
            return command_show()
        if args.command == "sync-tracker":
            return command_sync_tracker()
        return fail(f"unknown command: {args.command}", 2)
    except OrchestratorFailure as exc:
        return fail(str(exc), exc.code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
