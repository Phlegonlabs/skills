#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
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
    is_placeholder,
    non_placeholder_string,
    parse_int,
    parse_yaml_subset,
    read_yaml,
    require_file,
)

OS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = OS_ROOT.parent
DOCS = OS_ROOT / "documents"
PLACEHOLDER_PREFIX = "<fill"
WAIVER_FILE = DOCS / "waivers" / "active.yaml"
WAIVER_REQUIRED_FIELDS = (
    "waiver_id",
    "gate_id",
    "scope",
    "reason",
    "approved_by",
    "created_at",
    "expires_at",
    "plan_revision",
    "status",
)
HANDOFF_REQUIRED_FIELDS = (
    "plan_id",
    "plan_revision",
    "task_id",
    "milestone_id",
    "branch_or_worktree",
    "write_scope",
    "changed_surfaces",
    "validations_passed",
    "commit_ref",
    "next_owner",
    "remaining_risks",
)
TASK_REQUIRED_FIELDS = (
    "write_scope",
    "validation_profile",
    "implementation_steps",
    "entrypoints",
    "validation_commands",
)
MILESTONE_REQUIRED_FIELDS = (
    "capability",
    "goal",
    "depends_on",
    "parallel_policy",
    "acceptance_criteria",
    "validation_commands",
    "done_when",
    "failure_policy",
    "demo_flow",
    "exit_validation",
    "tasks",
    "status",
)
UI_PLAN_KEYS = ("wireframe_ref", "design_ref", "frontend_design_skill_required")
UI_VALIDATION_PROFILES = {"ui-path", "design-review"}
ACTIVE_TASK_STATUSES = {"pending", "ready", "in_progress"}
PLAN_UI_REQUIRED_FIELDS = ("design_validation_ref", "wireframe_ref", "design_ref", "frontend_design_skill_required")
PLAN_RELEASE_REQUIRED_FIELDS = ("deployment_ref", "runtime_ref", "release_ref")
PLAN_DECISION_REQUIRED_FIELDS = ("decision_refs",)
TASK_UI_REQUIRED_FIELDS = ("wireframe_ref", "design_ref")
TASK_RELEASE_REQUIRED_FIELDS = ("runtime_ref", "release_ref", "deploy_commands_ref", "rollback_note")
TASK_DECISION_REQUIRED_FIELDS = ("decision_refs",)
DESIGN_REVIEW_REQUIRED_FIELDS = (
    "review_id",
    "plan_id",
    "milestone_scope",
    "wireframe_ref",
    "design_ref",
    "frontend_design_skill",
    "design_source",
    "scenarios",
    "states_checked",
    "breakpoints_checked",
    "findings",
    "decision",
)
DESIGN_REVIEW_ALLOWED_DECISIONS = {"pending", "passed", "failed", "waived"}
AUDIT_REQUIRED_FIELDS = (
    "audit_id",
    "plan_id",
    "release_ref",
    "deploy_ref",
    "target_environment",
    "scope_modules",
    "status",
    "summary",
    "blocking_findings",
    "non_blocking_findings",
    "follow_up_required",
    "executed_checks",
    "manual_checks",
    "skipped_checks",
    "smoke_failures",
    "module_results",
)
AUDIT_MODULE_REQUIRED_FIELDS = (
    "module_id",
    "applicable",
    "smoke_required",
    "smoke_status",
    "deep_audit_status",
    "checks_run",
    "manual_checks",
    "findings",
    "blocking",
    "evidence_refs",
)
AUDIT_ALLOWED_STATUSES = {"pending", "running", "failed", "passed"}
AUDIT_SMOKE_ALLOWED_STATUSES = {"not_required", "pending", "passed", "failed", "skipped"}
AUDIT_DEEP_ALLOWED_STATUSES = {"pending", "passed", "failed", "skipped"}
NON_WAIVABLE_COMMANDS = {"check-final-audit-ready", "check-final-audit-pass", "check-release-signoff"}


class GuardFailure(RuntimeError):
    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


configure_context(error_type=GuardFailure, repo_root=REPO_ROOT, placeholder_prefix=PLACEHOLDER_PREFIX)


def resolve_repo_ref(ref: str) -> Path:
    return REPO_ROOT / ref


def has_unresolved_token(value: object) -> bool:
    return isinstance(value, str) and re.search(r"\$\{[A-Za-z0-9_.-]+\}", value) is not None


def task_validation_evidence(task_id: str) -> list[dict[str, object]]:
    history_dir = DOCS / "validation" / "history"
    if not history_dir.is_dir():
        return []
    evidence: list[dict[str, object]] = []
    for path in sorted(history_dir.glob(f"task-{task_id}-*.yaml")):
        try:
            data = read_yaml(path)
        except GuardFailure:
            continue
        if data.get("task_id") == task_id:
            evidence.append(data)
    return evidence


def resolve_runtime_provider() -> str:
    """Resolve runtime provider from inventory or deploy doc, defaulting to cloudflare."""
    inventory_path = DOCS / "inventory" / "current-state.yaml"
    if inventory_path.is_file():
        try:
            inv = read_yaml(inventory_path)
            runtime = as_mapping(inv.get("runtime"))
            provider = non_placeholder_string(runtime.get("provider"))
            if provider:
                return provider
        except GuardFailure:
            pass
    deploy_path = DOCS / "deploy" / "current.yaml"
    if deploy_path.is_file():
        try:
            deploy = read_yaml(deploy_path)
            provider = non_placeholder_string(deploy.get("provider"))
            if provider:
                return provider
        except GuardFailure:
            pass
    return "cloudflare"


def plan_files() -> list[Path]:
    plan_dir = DOCS / "plans"
    if not plan_dir.is_dir():
        return []
    return sorted(plan_dir.glob("*.yaml"))


def plan_ready(data: dict[str, object]) -> bool:
    execution_ready = as_mapping(data.get("execution_ready"))
    review = as_mapping(data.get("review"))
    return (
        data.get("status") == "approved"
        and execution_ready.get("self_review_passed") is True
        and review.get("approved_for_execution") is True
    )


def current_plan_pointer() -> tuple[str | None, int | None]:
    status_path = DOCS / "status" / "current.yaml"
    if not status_path.is_file():
        return None, None
    status_data = read_yaml(status_path)
    plan_id = non_placeholder_string(status_data.get("plan_id"))
    raw_revision = status_data.get("plan_revision")
    return plan_id, parse_int(raw_revision)


def approved_plan_candidates() -> list[tuple[Path, dict[str, object]]]:
    candidates: list[tuple[Path, dict[str, object]]] = []
    for path in plan_files():
        try:
            data = read_yaml(path)
        except GuardFailure:
            continue
        if plan_ready(data):
            candidates.append((path, data))
    return candidates


def current_plan_candidate() -> tuple[Path, dict[str, object]] | None:
    plan_id, _ = current_plan_pointer()
    if plan_id:
        path = DOCS / "plans" / f"{plan_id}.yaml"
        if not path.is_file():
            raise GuardFailure(f"harnass-os/documents/status/current.yaml references missing plan file: {path}", 2)
        data = read_yaml(path)
        if data.get("id") != plan_id:
            raise GuardFailure(
                "harnass-os/documents/status/current.yaml "
                f"plan_id '{plan_id}' does not match plan file id '{data.get('id')}'",
                2,
            )
        return path, data

    candidates: list[tuple[Path, dict[str, object]]] = []
    for path in plan_files():
        try:
            data = read_yaml(path)
        except GuardFailure:
            continue
        candidates.append((path, data))
    if not candidates:
        return None
    if len(candidates) > 1:
        raise GuardFailure(
            "multiple plan files exist but harnass-os/documents/status/current.yaml does not point to one",
            2,
        )
    return candidates[0]


def select_approved_plan() -> tuple[Path, dict[str, object]] | None:
    plan_id, plan_revision = current_plan_pointer()
    if plan_id:
        path = DOCS / "plans" / f"{plan_id}.yaml"
        if not path.is_file():
            raise GuardFailure(f"harnass-os/documents/status/current.yaml references missing plan file: {path}", 2)
        data = read_yaml(path)
        if data.get("id") != plan_id:
            raise GuardFailure(
                "harnass-os/documents/status/current.yaml "
                f"plan_id '{plan_id}' does not match plan file id '{data.get('id')}'",
                2,
            )
        if not plan_ready(data):
            raise GuardFailure(
                "harnass-os/documents/status/current.yaml references a plan that is not approved for execution", 1
            )
        if plan_revision is not None:
            change_log = as_mapping(data.get("change_log"))
            if change_log.get("revision") != plan_revision:
                raise GuardFailure(
                    "harnass-os/documents/status/current.yaml plan_revision does not match plan.change_log.revision",
                    2,
                )
        return path, data

    candidates = approved_plan_candidates()
    if not candidates:
        return None
    if len(candidates) > 1:
        raise GuardFailure(
            "multiple approved plans exist but harnass-os/documents/status/current.yaml does not point to one",
            2,
        )
    return candidates[0]


def require_approved_plan(missing_message: str) -> tuple[Path, dict[str, object]]:
    result = select_approved_plan()
    if result is None:
        raise GuardFailure(missing_message, 1)
    return result


def require_current_plan(missing_message: str) -> tuple[Path, dict[str, object]]:
    result = current_plan_candidate()
    if result is None:
        raise GuardFailure(missing_message, 1)
    return result


def git_output(*args: str) -> tuple[int, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout


def staged_file_diff_exists(path: Path) -> bool:
    relative_path = path.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", relative_path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise GuardFailure("unable to inspect staged plan changes", 2)
    return result.returncode == 1


def read_head_yaml(path: Path) -> dict[str, object] | None:
    relative_path = path.relative_to(REPO_ROOT).as_posix()
    code, stdout = git_output("show", f"HEAD:{relative_path}")
    if code != 0:
        return None
    data = parse_yaml_subset(stdout)
    if not isinstance(data, dict):
        raise GuardFailure(f"expected a yaml mapping in HEAD:{relative_path}", 2)
    return data


def extract_tasks(data: dict[str, object]) -> list[dict[str, object]]:
    raw_tasks = data.get("tasks")
    if not isinstance(raw_tasks, list):
        raise GuardFailure("approved plan must define top-level tasks", 1)

    tasks: list[dict[str, object]] = []
    task_ids: set[str] = set()
    for item in raw_tasks:
        if not isinstance(item, dict):
            raise GuardFailure("plan.tasks must be a list of task objects", 1)
        task = dict(item)
        tid = non_placeholder_string(task.get("id"))
        if tid is None:
            raise GuardFailure("every task in plan.tasks must define a non-placeholder id", 1)
        if tid in task_ids:
            raise GuardFailure(f"duplicate task id: {tid}", 1)
        task_ids.add(tid)
        tasks.append(task)

    raw_milestones = data.get("milestones")
    if not isinstance(raw_milestones, list):
        raise GuardFailure("approved plan must define milestones", 1)

    task_to_milestone: dict[str, str] = {}
    for milestone_obj in raw_milestones:
        if not isinstance(milestone_obj, dict):
            raise GuardFailure("plan.milestones must be a list of milestone objects", 1)
        milestone_id = non_placeholder_string(milestone_obj.get("id"))
        if milestone_id is None:
            raise GuardFailure("every milestone must define a non-placeholder id", 1)
        refs = milestone_obj.get("tasks")
        if not isinstance(refs, list):
            raise GuardFailure(f"milestone {milestone_id}: tasks must be a list of task ids", 1)
        for ref in refs:
            task_id = non_placeholder_string(ref)
            if task_id is None:
                raise GuardFailure(f"milestone {milestone_id}: tasks contains an empty or placeholder task id", 1)
            if task_id not in task_ids:
                raise GuardFailure(f"milestone {milestone_id}: references unknown task '{task_id}'", 1)
            owner = task_to_milestone.get(task_id)
            if owner is not None and owner != milestone_id:
                raise GuardFailure(f"task {task_id}: referenced by multiple milestones ({owner}, {milestone_id})", 1)
            task_to_milestone[task_id] = milestone_id

    for task in tasks:
        tid = str(task["id"])
        milestone_id = task_to_milestone.get(tid)
        if milestone_id is None:
            raise GuardFailure(f"task {tid}: not referenced by any milestone", 1)
        task["milestone_id"] = milestone_id
    return tasks


def validate_milestones(data: dict[str, object], task_ids: set[str]) -> list[str]:
    raw_milestones = data.get("milestones")
    if not isinstance(raw_milestones, list):
        return ["approved plan must define milestones"]

    errors: list[str] = []
    for milestone_obj in raw_milestones:
        if not isinstance(milestone_obj, dict):
            errors.append("plan.milestones must be a list of milestone objects")
            continue
        milestone_id = non_placeholder_string(milestone_obj.get("id")) or "unknown"
        for field in MILESTONE_REQUIRED_FIELDS:
            value = milestone_obj.get(field)
            if value is None:
                errors.append(f"milestone {milestone_id}: missing required field '{field}'")
            elif isinstance(value, list) and len(value) == 0 and field != "depends_on":
                errors.append(f"milestone {milestone_id}: field '{field}' is empty")
            elif is_placeholder(value):
                errors.append(f"milestone {milestone_id}: field '{field}' is still <fill>")

        refs = milestone_obj.get("tasks")
        if isinstance(refs, list):
            for ref in refs:
                task_id = non_placeholder_string(ref)
                if task_id is None:
                    errors.append(f"milestone {milestone_id}: tasks contains an empty or placeholder task id")
                elif task_id not in task_ids:
                    errors.append(f"milestone {milestone_id}: references unknown task '{task_id}'")
    return errors


def plan_has_ui_surface(data: dict[str, object], tasks: list[dict[str, object]]) -> bool:
    if any(key in data for key in UI_PLAN_KEYS):
        return True
    inventory_path = DOCS / "inventory" / "current-state.yaml"
    if inventory_path.is_file():
        try:
            inventory_data = read_yaml(inventory_path)
        except GuardFailure:
            inventory_data = {}
        if inventory_data.get("ui_facing") is True:
            return True
    for task in tasks:
        if task.get("validation_profile") in UI_VALIDATION_PROFILES:
            return True
        if task.get("wireframe_ref") or task.get("design_ref"):
            return True
    return False


def plan_is_release_affecting(data: dict[str, object], tasks: list[dict[str, object]]) -> bool:
    if data.get("release_affecting") is True:
        return True
    for task in tasks:
        if any(task.get(field) for field in TASK_RELEASE_REQUIRED_FIELDS):
            return True
        for path in as_string_list(task.get("write_scope")):
            if (
                path == "harnass-os/documents/deploy/current.yaml"
                or path == "harnass-os/documents/release/current.yaml"
                or path.startswith("harnass-os/documents/runtime/")
            ):
                return True
    return False


def plan_is_decision_sensitive(data: dict[str, object], tasks: list[dict[str, object]]) -> bool:
    if data.get("decision_sensitive") is True:
        return True
    return any(task.get("decision_refs") for task in tasks)


def validate_required_fields(
    label: str,
    values: dict[str, object],
    fields: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    for field in fields:
        value = values.get(field)
        if value is None:
            errors.append(f"{label}: missing required field '{field}'")
        elif isinstance(value, list) and len(value) == 0:
            errors.append(f"{label}: field '{field}' is empty")
        elif is_placeholder(value):
            errors.append(f"{label}: field '{field}' is still <fill>")
    return errors


def validate_design_review(plan_data: dict[str, object], allow_pending: bool) -> list[str]:
    review_path = DOCS / "validation" / "design-review.yaml"
    require_file(review_path, "harnass-os/documents/validation/design-review.yaml")
    review_data = read_yaml(review_path)
    required_without_findings = tuple(field for field in DESIGN_REVIEW_REQUIRED_FIELDS if field != "findings")
    errors = validate_required_fields("design-review", review_data, required_without_findings)
    findings = review_data.get("findings")
    if findings is None:
        errors.append("design-review: missing required field 'findings'")
    elif not isinstance(findings, list):
        errors.append("design-review: field 'findings' must be a list")
    decision = review_data.get("decision")
    if decision not in DESIGN_REVIEW_ALLOWED_DECISIONS:
        errors.append("design-review: decision must be one of pending, passed, failed, or waived")
    elif not allow_pending and decision not in {"passed", "waived"}:
        errors.append("design-review: decision must be passed or waived before execution")

    plan_id = non_placeholder_string(plan_data.get("id"))
    if plan_id is not None and review_data.get("plan_id") != plan_id:
        errors.append(f"design-review: plan_id must match plan id '{plan_id}'")
    if review_data.get("wireframe_ref") != "harnass-os/documents/design/wireframe.md":
        errors.append("design-review: wireframe_ref must point to harnass-os/documents/design/wireframe.md")
    if review_data.get("design_ref") != "harnass-os/documents/design/design.md":
        errors.append("design-review: design_ref must point to harnass-os/documents/design/design.md")
    if review_data.get("frontend_design_skill") != "frontend-design":
        errors.append("design-review: frontend_design_skill must be frontend-design")
    return errors


def load_waivers() -> list[dict[str, object]]:
    if not WAIVER_FILE.is_file():
        return []
    try:
        data = read_yaml(WAIVER_FILE)
    except GuardFailure:
        return []
    raw = data.get("waivers")
    if not isinstance(raw, list):
        return []
    return [w for w in raw if isinstance(w, dict)]


def is_gate_waived(gate_id: str, scope: str) -> dict[str, object] | None:
    _, plan_revision = current_plan_pointer()
    for waiver in load_waivers():
        if waiver.get("gate_id") != gate_id:
            continue
        if waiver.get("scope") != scope:
            continue
        if waiver.get("status") != "active":
            continue
        if plan_revision is not None and waiver.get("plan_revision") != plan_revision:
            continue
        return waiver
    return None


def warn_waived(gate_id: str, waiver: dict[str, object]) -> None:
    reason = waiver.get("reason", "no reason given")
    print(f"GATE WAIVED: {gate_id} -- reason: {reason}", file=sys.stderr)


def read_audit_current() -> dict[str, object]:
    return read_yaml(DOCS / "audit" / "current.yaml")


def validate_audit_module_results(module_results: list[object], *, require_passed: bool) -> list[str]:
    errors: list[str] = []
    for index, raw_module in enumerate(module_results):
        if not isinstance(raw_module, dict):
            errors.append(f"audit.module_results[{index}] must be a mapping")
            continue
        module = raw_module
        module_id = non_placeholder_string(module.get("module_id")) or f"module[{index}]"
        for field in AUDIT_MODULE_REQUIRED_FIELDS:
            value = module.get(field)
            if value is None:
                errors.append(f"audit {module_id}: missing required field '{field}'")
                continue
            if (
                isinstance(value, str)
                and non_placeholder_string(value) is None
                and field
                in {
                    "module_id",
                    "smoke_status",
                    "deep_audit_status",
                }
            ):
                errors.append(f"audit {module_id}: field '{field}' is empty or still <fill>")

        applicable = module.get("applicable")
        if not isinstance(applicable, bool):
            errors.append(f"audit {module_id}: applicable must be true or false")

        smoke_required = module.get("smoke_required")
        if not isinstance(smoke_required, bool):
            errors.append(f"audit {module_id}: smoke_required must be true or false")

        smoke_status = module.get("smoke_status")
        if smoke_status not in AUDIT_SMOKE_ALLOWED_STATUSES:
            errors.append(
                f"audit {module_id}: smoke_status must be one of {', '.join(sorted(AUDIT_SMOKE_ALLOWED_STATUSES))}"
            )

        deep_status = module.get("deep_audit_status")
        if deep_status not in AUDIT_DEEP_ALLOWED_STATUSES:
            errors.append(
                f"audit {module_id}: deep_audit_status must be one of {', '.join(sorted(AUDIT_DEEP_ALLOWED_STATUSES))}"
            )

        if not isinstance(module.get("checks_run"), list):
            errors.append(f"audit {module_id}: checks_run must be a list")
        if not isinstance(module.get("manual_checks"), list):
            errors.append(f"audit {module_id}: manual_checks must be a list")
        if not isinstance(module.get("findings"), list):
            errors.append(f"audit {module_id}: findings must be a list")
        if not isinstance(module.get("evidence_refs"), list):
            errors.append(f"audit {module_id}: evidence_refs must be a list")
        if not isinstance(module.get("blocking"), bool):
            errors.append(f"audit {module_id}: blocking must be true or false")

        if require_passed and applicable is True:
            if smoke_required is True and smoke_status != "passed":
                errors.append(f"audit {module_id}: smoke_required module must have smoke_status=passed")
            if smoke_required is False and smoke_status not in {"not_required", "skipped", "passed"}:
                errors.append(f"audit {module_id}: non-smoke module must not keep a failing smoke_status")
            if deep_status != "passed":
                errors.append(f"audit {module_id}: applicable module must have deep_audit_status=passed")
            if module.get("blocking") is not False:
                errors.append(f"audit {module_id}: applicable module cannot remain blocking when audit passes")
    return errors


def final_audit_pass_errors(audit: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for field in AUDIT_REQUIRED_FIELDS:
        if field not in audit:
            errors.append(f"audit: missing required field '{field}'")

    for field in ("audit_id", "plan_id", "release_ref", "deploy_ref", "target_environment", "status", "summary"):
        value = non_placeholder_string(audit.get(field))
        if value is None:
            errors.append(f"audit: field '{field}' must be a non-placeholder string")

    if audit.get("release_ref") != "harnass-os/documents/release/current.yaml":
        errors.append("audit: release_ref must point to harnass-os/documents/release/current.yaml")
    if audit.get("deploy_ref") != "harnass-os/documents/deploy/current.yaml":
        errors.append("audit: deploy_ref must point to harnass-os/documents/deploy/current.yaml")
    if audit.get("target_environment") != "production":
        errors.append("audit: target_environment must be production")
    if audit.get("status") not in AUDIT_ALLOWED_STATUSES:
        errors.append(f"audit: status must be one of {', '.join(sorted(AUDIT_ALLOWED_STATUSES))}")
    if audit.get("status") != "passed":
        errors.append("audit: status must be passed before release signoff")

    for field in (
        "scope_modules",
        "blocking_findings",
        "non_blocking_findings",
        "executed_checks",
        "manual_checks",
        "skipped_checks",
        "smoke_failures",
        "module_results",
    ):
        if not isinstance(audit.get(field), list):
            errors.append(f"audit: field '{field}' must be a list")

    if not isinstance(audit.get("follow_up_required"), bool):
        errors.append("audit: follow_up_required must be true or false")

    scope_modules = as_string_list(audit.get("scope_modules"))
    if not scope_modules:
        errors.append("audit: scope_modules must include at least one applicable module")
    module_results = as_list(audit.get("module_results"))
    if not module_results:
        errors.append("audit: module_results must include at least one module result")

    blocking_findings = as_list(audit.get("blocking_findings"))
    if blocking_findings:
        errors.append("audit: blocking_findings must be empty before release signoff")
    smoke_failures = as_list(audit.get("smoke_failures"))
    if smoke_failures:
        errors.append("audit: smoke_failures must be empty before release signoff")
    if audit.get("follow_up_required") is not False:
        errors.append("audit: follow_up_required must be false before release signoff")

    errors.extend(validate_audit_module_results(module_results, require_passed=True))
    return errors


def command_classify_intake_horizon(_: list[str]) -> int:
    intake_data = read_yaml(DOCS / "intake" / "request.yaml")
    if "initial_horizon" not in intake_data:
        raise GuardFailure("intake file must define initial_horizon", 2)
    return 0


def command_seed_execution_state(_: list[str]) -> int:
    require_file(DOCS / "runs" / "current.yaml", "harnass-os/documents/runs/current.yaml")
    require_file(DOCS / "status" / "current.yaml", "harnass-os/documents/status/current.yaml")
    return 0


def command_confirm_plan_horizon(_: list[str]) -> int:
    _, data = require_approved_plan("no approved plan available to confirm task_horizon")
    if "task_horizon" not in data:
        raise GuardFailure("approved plan must define task_horizon", 1)
    return 0


def command_check_plan_review(_: list[str]) -> int:
    _, data = require_approved_plan("no approved plan available for review check")
    review = as_mapping(data.get("review"))
    if review.get("approved_for_execution") is not True:
        raise GuardFailure("approved plan review must set approved_for_execution: true", 1)
    return 0


def command_check_plan_gate(_: list[str]) -> int:
    require_approved_plan("execution is blocked until an approved execution-ready plan exists")
    return 0


def command_record_task_change(_: list[str]) -> int:
    plan_path, data = require_current_plan("task shape changes require a current plan revision")
    change_log = as_mapping(data.get("change_log"))
    if "revision" not in change_log:
        raise GuardFailure("task shape changes require an approved plan revision", 1)
    if not staged_file_diff_exists(plan_path):
        return 0

    previous = read_head_yaml(plan_path)
    if previous is None:
        return 0

    task_shape_changed = previous.get("tasks") != data.get("tasks") or previous.get("milestones") != data.get(
        "milestones"
    )
    if not task_shape_changed:
        return 0

    previous_revision = parse_int(as_mapping(previous.get("change_log")).get("revision"))
    current_revision = parse_int(change_log.get("revision"))
    if previous_revision is None or current_revision is None:
        raise GuardFailure("task shape changes require numeric change_log.revision values", 1)
    if current_revision <= previous_revision:
        raise GuardFailure(
            "task shape changes require incrementing plan.change_log.revision before commit",
            1,
        )
    return 0


def command_check_task_sync(_: list[str]) -> int:
    require_file(DOCS / "status" / "current.yaml", "harnass-os/documents/status/current.yaml")
    handoff_dir = DOCS / "handoffs"
    if not handoff_dir.is_dir():
        raise GuardFailure("missing required directory: harnass-os/documents/handoffs", 2)
    _, data = require_approved_plan("no approved plan to check task sync against")
    tasks = extract_tasks(data)
    status_data = read_yaml(DOCS / "status" / "current.yaml")

    task_ids = {str(task["id"]) for task in tasks}
    completed_ids = as_string_list(status_data.get("completed"))
    next_task = non_placeholder_string(status_data.get("next"))
    errors: list[str] = []

    for task_id in completed_ids:
        if task_id not in task_ids:
            errors.append(f"status/current.yaml completed references unknown task '{task_id}'")

    if next_task is not None and next_task not in task_ids:
        errors.append(f"status/current.yaml next references unknown task '{next_task}'")

    for task in tasks:
        tid = str(task["id"])
        status = task.get("status")
        handoff_ref = non_placeholder_string(task.get("handoff_output"))
        if status == "committed":
            if handoff_ref is None:
                errors.append(f"task {tid}: committed status requires handoff_output")
                continue
            handoff_path = resolve_repo_ref(handoff_ref)
            if not handoff_path.is_file() or not handoff_is_ready(handoff_path):
                errors.append(f"task {tid}: committed status requires a valid handoff at {handoff_ref}")
        if tid in completed_ids and status != "committed":
            errors.append(f"task {tid}: listed in status/current.yaml completed but plan status is {status}")
        if next_task == tid and status == "committed":
            errors.append(f"task {tid}: cannot be next when already committed")

    if errors:
        raise GuardFailure("task sync check failed:\n  " + "\n  ".join(errors), 1)
    return 0


def handoff_is_ready(path: Path) -> bool:
    try:
        data = read_yaml(path)
    except GuardFailure:
        return False
    for field in HANDOFF_REQUIRED_FIELDS:
        value = data.get(field)
        if value is None or is_placeholder(value):
            return False
        if (
            field in {"write_scope", "changed_surfaces", "validations_passed"}
            and isinstance(value, list)
            and len(value) == 0
        ):
            return False
        if isinstance(value, str) and not value.strip():
            return False
    return True


def command_check_handoff_ready(_: list[str]) -> int:
    handoff_dir = DOCS / "handoffs"
    if not handoff_dir.is_dir():
        raise GuardFailure("missing required directory: harnass-os/documents/handoffs", 2)
    _, data = require_approved_plan("push is blocked until an approved execution-ready plan exists")
    tasks = extract_tasks(data)
    committed_tasks = [task for task in tasks if task.get("status") == "committed"]
    if not committed_tasks:
        raise GuardFailure("push is blocked until at least one committed task exists in the approved plan", 1)

    valid_handoffs: dict[str, Path] = {}
    for path in sorted(handoff_dir.glob("*.yaml")):
        if not handoff_is_ready(path):
            continue
        handoff_data = read_yaml(path)
        task_id = non_placeholder_string(handoff_data.get("task_id"))
        if task_id is not None:
            valid_handoffs[task_id] = path

    missing: list[str] = []
    for task in committed_tasks:
        tid = str(task["id"])
        if tid not in valid_handoffs:
            handoff_ref = (
                non_placeholder_string(task.get("handoff_output")) or "harnass-os/documents/handoffs/<task-id>.yaml"
            )
            missing.append(f"task {tid}: missing valid handoff at {handoff_ref}")
    if missing:
        raise GuardFailure(
            "push is blocked until every committed task has a valid handoff:\n  " + "\n  ".join(missing), 1
        )
    return 0


def command_check_execution_ready(_: list[str]) -> int:
    require_file(DOCS / "validation" / "profiles.yaml", "harnass-os/documents/validation/profiles.yaml")
    _, plan_data = require_approved_plan("execution is blocked until an approved execution-ready plan exists")
    execution_ready = as_mapping(plan_data.get("execution_ready"))
    if execution_ready.get("task_docs_synced") is not True:
        raise GuardFailure("execution is blocked until task_docs_synced is true", 1)
    tasks = extract_tasks(plan_data)
    task_ids = {str(task["id"]) for task in tasks}
    errors = validate_milestones(plan_data, task_ids)

    is_ui_plan = plan_has_ui_surface(plan_data, tasks)
    if is_ui_plan:
        errors.extend(validate_required_fields("plan", plan_data, PLAN_UI_REQUIRED_FIELDS))
        for path, label in (
            (DOCS / "design" / "wireframe.md", "harnass-os/documents/design/wireframe.md"),
            (DOCS / "design" / "design.md", "harnass-os/documents/design/design.md"),
        ):
            require_file(path, label)
        errors.extend(validate_design_review(plan_data, allow_pending=False))

    if plan_is_release_affecting(plan_data, tasks):
        errors.extend(validate_required_fields("plan", plan_data, PLAN_RELEASE_REQUIRED_FIELDS))
        provider = resolve_runtime_provider()
        runtime_file = f"harnass-os/documents/runtime/{provider}.yaml"
        for path, label in (
            (DOCS / "deploy" / "current.yaml", "harnass-os/documents/deploy/current.yaml"),
            (DOCS / "runtime" / f"{provider}.yaml", runtime_file),
            (DOCS / "release" / "current.yaml", "harnass-os/documents/release/current.yaml"),
        ):
            require_file(path, label)

    if plan_is_decision_sensitive(plan_data, tasks):
        errors.extend(validate_required_fields("plan", plan_data, PLAN_DECISION_REQUIRED_FIELDS))
        require_file(DOCS / "decisions" / "index.yaml", "harnass-os/documents/decisions/index.yaml")

    if errors:
        raise GuardFailure("execution readiness check failed:\n  " + "\n  ".join(errors), 1)
    return 0


def command_check_deployment_ready(_: list[str]) -> int:
    deploy = read_yaml(DOCS / "deploy" / "current.yaml")
    provider = resolve_runtime_provider()
    read_yaml(DOCS / "runtime" / f"{provider}.yaml")
    release = read_yaml(DOCS / "release" / "current.yaml")
    read_yaml(DOCS / "status" / "current.yaml")

    state = deploy.get("status", "draft")
    preview_validation = as_mapping(deploy.get("preview_validation"))
    smoke_command_refs = as_list(deploy.get("smoke_command_refs"))

    if state in {"preview_validated", "production_ready", "deployed"} and preview_validation.get("status") != "passed":
        raise GuardFailure("deployment is blocked until preview validation passes", 1)
    if state in {"production_ready", "deployed", "rollback_required"} and not deploy.get("rollback_strategy"):
        raise GuardFailure("deployment is blocked until rollback_strategy is documented", 1)
    if state in {"production_ready", "deployed", "rollback_required"} and not deploy.get("rollback_command"):
        raise GuardFailure("deployment is blocked until rollback_command is documented", 1)
    if state in {"production_ready", "deployed", "rollback_required"} and not deploy.get("preview_deploy_command"):
        raise GuardFailure("deployment is blocked until preview_deploy_command is documented", 1)
    if state in {"production_ready", "deployed", "rollback_required"} and not deploy.get("production_deploy_command"):
        raise GuardFailure("deployment is blocked until production_deploy_command is documented", 1)
    if state in {"production_ready", "deployed", "rollback_required"} and not smoke_command_refs:
        raise GuardFailure("deployment is blocked until smoke_command_refs are documented", 1)
    if state in {"production_ready", "deployed", "rollback_required"} and release.get("status") not in {
        "preview_passed",
        "production_ready",
        "released",
        "audit_pending",
        "audit_failed",
        "complete",
    }:
        raise GuardFailure(
            "deployment is blocked until the release document records "
            "preview_passed, production_ready, or an audit-aware release state",
            1,
        )
    return 0


def command_check_final_audit_ready(_: list[str]) -> int:
    deploy = read_yaml(DOCS / "deploy" / "current.yaml")
    provider = resolve_runtime_provider()
    read_yaml(DOCS / "runtime" / f"{provider}.yaml")
    release = read_yaml(DOCS / "release" / "current.yaml")
    read_yaml(DOCS / "status" / "current.yaml")
    audit = read_audit_current()

    if deploy.get("post_deploy_audit_required") is not True:
        raise GuardFailure("final audit is blocked until deploy.current.post_deploy_audit_required is true", 1)

    deploy_state = deploy.get("status", "draft")
    release_state = release.get("status", "draft")
    if deploy_state not in {"deployed", "rollback_required"}:
        raise GuardFailure("final audit is blocked until production deployment is recorded in deploy.current.status", 1)

    if release_state not in {
        "released",
        "audit_pending",
        "audit_failed",
        "complete",
    }:
        raise GuardFailure("final audit is blocked until release.current.status reflects a post-production state", 1)

    if release.get("final_audit_ref") != "harnass-os/documents/audit/current.yaml":
        raise GuardFailure(
            "final audit is blocked until release.current.final_audit_ref "
            "points to harnass-os/documents/audit/current.yaml",
            1,
        )

    if audit.get("target_environment") != "production":
        raise GuardFailure("final audit is blocked until audit.current.target_environment is production", 1)
    return 0


def command_check_final_audit_pass(_: list[str]) -> int:
    errors = final_audit_pass_errors(read_audit_current())
    if errors:
        raise GuardFailure("final audit pass check failed:\n  " + "\n  ".join(errors), 1)
    return 0


def command_check_release_signoff(_: list[str]) -> int:
    deploy = read_yaml(DOCS / "deploy" / "current.yaml")
    release = read_yaml(DOCS / "release" / "current.yaml")
    read_yaml(DOCS / "status" / "current.yaml")

    if deploy.get("post_deploy_audit_required") is not True:
        raise GuardFailure("release signoff is blocked until post_deploy_audit_required is true", 1)

    errors = final_audit_pass_errors(read_audit_current())
    if release.get("final_audit_ref") != "harnass-os/documents/audit/current.yaml":
        errors.append("release: final_audit_ref must point to harnass-os/documents/audit/current.yaml")
    if release.get("final_audit_status") != "passed":
        errors.append("release: final_audit_status must be passed before release signoff")
    if release.get("status") != "complete":
        errors.append("release: status must be complete before release signoff")

    if errors:
        raise GuardFailure("release signoff check failed:\n  " + "\n  ".join(errors), 1)
    return 0


def command_check_commit_context(args: list[str]) -> int:
    if len(args) != 1:
        raise GuardFailure("check-commit-context expects the commit message file path", 2)
    message_path = Path(args[0])
    require_file(message_path, "commit message")
    message = message_path.read_text(encoding="utf-8")
    if not re.search(r"\b(task|plan):[A-Za-z0-9._/\-]+\b", message):
        raise GuardFailure("commit messages must include task:<id> or plan:<revision> context", 1)
    return 0


def command_check_task_fields(_: list[str]) -> int:
    _, data = require_approved_plan("no approved plan to check task fields against")
    tasks = extract_tasks(data)
    if not tasks:
        raise GuardFailure("approved plan has no tasks defined in plan.tasks", 1)

    ui_plan = plan_has_ui_surface(data, tasks)
    release_plan = plan_is_release_affecting(data, tasks)
    decision_plan = plan_is_decision_sensitive(data, tasks)
    errors: list[str] = []
    for task in tasks:
        tid = task.get("id", "unknown")
        for field in TASK_REQUIRED_FIELDS:
            value = task.get(field)
            if value is None:
                errors.append(f"task {tid}: missing required field '{field}'")
            elif isinstance(value, list) and len(value) == 0:
                errors.append(f"task {tid}: field '{field}' is empty")
            elif is_placeholder(value):
                errors.append(f"task {tid}: field '{field}' is still <fill>")
        entrypoints = as_list(task.get("entrypoints"))
        for index, entry in enumerate(entrypoints, 1):
            if not isinstance(entry, dict):
                errors.append(f"task {tid}: entrypoints[{index}] must be an object with file and reason")
                continue
            if non_placeholder_string(entry.get("file")) is None:
                errors.append(f"task {tid}: entrypoints[{index}].file is missing or placeholder")
            if non_placeholder_string(entry.get("reason")) is None:
                errors.append(f"task {tid}: entrypoints[{index}].reason is missing or placeholder")
        for command in as_string_list(task.get("validation_commands")):
            if has_unresolved_token(command):
                errors.append(f"task {tid}: validation_commands must not retain unresolved ${'{'}...{'}'} tokens")

        if task.get("validation_profile") in UI_VALIDATION_PROFILES or ui_plan:
            if task.get("validation_profile") in UI_VALIDATION_PROFILES:
                errors.extend(validate_required_fields(f"task {tid}", task, TASK_UI_REQUIRED_FIELDS))
        if release_plan and any(
            task.get(field) for field in ("runtime_ref", "release_ref", "deploy_commands_ref", "rollback_note")
        ):
            errors.extend(validate_required_fields(f"task {tid}", task, TASK_RELEASE_REQUIRED_FIELDS))
        if decision_plan and task.get("decision_refs") is not None:
            errors.extend(validate_required_fields(f"task {tid}", task, TASK_DECISION_REQUIRED_FIELDS))
    if errors:
        raise GuardFailure("task field validation failed:\n  " + "\n  ".join(errors), 1)
    return 0


def command_check_design_sync(_: list[str]) -> int:
    inventory_data = read_yaml(DOCS / "inventory" / "current-state.yaml")
    current_plan = current_plan_candidate()
    plan_data = current_plan[1] if current_plan is not None else {}
    tasks = extract_tasks(plan_data) if plan_data else []
    if inventory_data.get("ui_facing") is not True and not plan_has_ui_surface(plan_data, tasks):
        return 0

    wireframe = DOCS / "design" / "wireframe.md"
    design = DOCS / "design" / "design.md"
    errors: list[str] = []
    if not wireframe.is_file():
        errors.append("missing harnass-os/documents/design/wireframe.md (required for UI-facing plan)")
    elif wireframe.stat().st_size < 50:
        errors.append("harnass-os/documents/design/wireframe.md appears empty or placeholder-only")
    if not design.is_file():
        errors.append("missing harnass-os/documents/design/design.md (required for UI-facing plan)")
    elif design.stat().st_size < 50:
        errors.append("harnass-os/documents/design/design.md appears empty or placeholder-only")

    if plan_data:
        errors.extend(validate_required_fields("plan", plan_data, PLAN_UI_REQUIRED_FIELDS))

    for task in tasks:
        tid = task.get("id", "unknown")
        if task.get("validation_profile") in UI_VALIDATION_PROFILES:
            errors.extend(validate_required_fields(f"task {tid}", task, TASK_UI_REQUIRED_FIELDS))

    if errors:
        raise GuardFailure("design sync check failed:\n  " + "\n  ".join(errors), 1)

    if plan_data:
        review_errors = validate_design_review(plan_data, allow_pending=True)
        if review_errors:
            raise GuardFailure("design sync check failed:\n  " + "\n  ".join(review_errors), 1)

    return 0


def command_check_write_scope_overlap(_: list[str]) -> int:
    _, data = require_approved_plan("no approved plan to check write scope overlap")
    active_scopes: dict[str, list[str]] = {}
    for task in extract_tasks(data):
        status = task.get("status", "pending")
        if status not in ACTIVE_TASK_STATUSES:
            continue
        tid = str(task.get("id", "unknown"))
        for item in as_string_list(task.get("write_scope")):
            active_scopes.setdefault(item, []).append(tid)

    overlaps = [f"  {scope}: shared by {', '.join(tids)}" for scope, tids in active_scopes.items() if len(tids) > 1]
    if overlaps:
        raise GuardFailure("write_scope overlap detected (parallel conflict risk):\n" + "\n".join(overlaps), 1)
    return 0


def command_check_task_deps(_: list[str]) -> int:
    _, data = require_approved_plan("no approved plan to check task dependencies")
    tasks = extract_tasks(data)
    task_ids = {str(task.get("id", "")) for task in tasks}
    errors: list[str] = []
    graph: dict[str, list[str]] = {}

    for task in tasks:
        tid = str(task.get("id", "unknown"))
        dep_list = as_string_list(task.get("depends_on"))
        graph[tid] = dep_list
        for dep in dep_list:
            if dep not in task_ids:
                errors.append(f"task {tid}: depends_on references non-existent task '{dep}'")

    white, gray, black = 0, 1, 2
    color: dict[str, int] = {tid: white for tid in graph}

    def dfs(node: str, path: list[str]) -> bool:
        color[node] = gray
        path.append(node)
        for dep in graph.get(node, []):
            if dep not in color:
                continue
            if color[dep] == gray:
                cycle_start = path.index(dep)
                cycle = path[cycle_start:] + [dep]
                errors.append(f"dependency cycle detected: {' -> '.join(cycle)}")
                return True
            if color[dep] == white and dfs(dep, path):
                return True
        path.pop()
        color[node] = black
        return False

    for tid in graph:
        if color[tid] == white:
            dfs(tid, [])

    if errors:
        raise GuardFailure("task dependency check failed:\n  " + "\n  ".join(errors), 1)
    return 0


def command_check_validation_complete(_: list[str]) -> int:
    _, data = require_approved_plan("no approved plan to check validation completeness")
    errors: list[str] = []
    for task in extract_tasks(data):
        status = task.get("status")
        if status not in {"validated", "committed"}:
            continue
        tid = str(task.get("id", "unknown"))
        commands = task.get("validation_commands")
        if commands is None or (isinstance(commands, list) and len(commands) == 0):
            errors.append(f"task {tid}: status is {status} but has no validation_commands")
            continue
        for command in as_string_list(commands):
            if is_placeholder(command):
                errors.append(f"task {tid}: validation_commands contains unfilled <fill> placeholder")
            elif has_unresolved_token(command):
                errors.append(f"task {tid}: validation_commands contains unresolved ${'{'}...{'}'} token")
        evidence = task_validation_evidence(tid)
        if not evidence:
            errors.append(f"task {tid}: status is {status} but no validation evidence exists in validation/history")
            continue
        if not any(item.get("status") == "passed" for item in evidence):
            errors.append(f"task {tid}: validation evidence exists but no passing run was recorded")

    if errors:
        raise GuardFailure("validation completeness check failed:\n  " + "\n  ".join(errors), 1)
    return 0


def command_check_waiver_integrity(_: list[str]) -> int:
    waivers = load_waivers()
    if not waivers:
        return 0
    _, plan_revision = current_plan_pointer()
    errors: list[str] = []
    seen_ids: set[str] = set()
    for waiver in waivers:
        wid = non_placeholder_string(waiver.get("waiver_id")) or "unknown"
        if wid in seen_ids:
            errors.append(f"duplicate waiver_id: {wid}")
        seen_ids.add(wid)
        for field in WAIVER_REQUIRED_FIELDS:
            value = waiver.get(field)
            if value is None:
                errors.append(f"waiver {wid}: missing required field '{field}'")
            elif is_placeholder(value):
                errors.append(f"waiver {wid}: field '{field}' is still <fill>")
        status = waiver.get("status")
        if status not in {"active", "expired", "revoked"}:
            errors.append(f"waiver {wid}: invalid status '{status}'")
        if plan_revision is not None and waiver.get("status") == "active":
            if waiver.get("plan_revision") != plan_revision:
                errors.append(
                    "waiver {wid}: plan_revision mismatch "
                    "(waiver={waiver_revision}, current={current_revision})".format(
                        wid=wid,
                        waiver_revision=waiver.get("plan_revision"),
                        current_revision=plan_revision,
                    )
                )
    if errors:
        raise GuardFailure("waiver integrity check failed:\n  " + "\n  ".join(errors), 1)
    return 0


COMMANDS = {
    "classify-intake-horizon": command_classify_intake_horizon,
    "seed-execution-state": command_seed_execution_state,
    "confirm-plan-horizon": command_confirm_plan_horizon,
    "check-plan-review": command_check_plan_review,
    "check-plan-gate": command_check_plan_gate,
    "record-task-change": command_record_task_change,
    "check-task-sync": command_check_task_sync,
    "check-handoff-ready": command_check_handoff_ready,
    "check-execution-ready": command_check_execution_ready,
    "check-deployment-ready": command_check_deployment_ready,
    "check-final-audit-ready": command_check_final_audit_ready,
    "check-final-audit-pass": command_check_final_audit_pass,
    "check-release-signoff": command_check_release_signoff,
    "check-commit-context": command_check_commit_context,
    "check-task-fields": command_check_task_fields,
    "check-design-sync": command_check_design_sync,
    "check-write-scope-overlap": command_check_write_scope_overlap,
    "check-task-deps": command_check_task_deps,
    "check-validation-complete": command_check_validation_complete,
    "check-waiver-integrity": command_check_waiver_integrity,
}


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return fail(f"usage: {argv[0]} <command> [args...]", 2)
    command = argv[1]
    handler = COMMANDS.get(command)
    if handler is None:
        return fail(f"unknown command: {command}", 2)
    try:
        return handler(argv[2:])
    except GuardFailure as error:
        if command not in NON_WAIVABLE_COMMANDS:
            waiver = is_gate_waived(command, "global")
            if waiver is not None:
                warn_waived(command, waiver)
                return 0
        return fail(str(error), error.code)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
