#!/usr/bin/env python3
"""Materialize the target repo scaffold from the local start skill."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SUITE_ROOT = SKILL_ROOT.parent
BOOTSTRAP_SCHEMA = SKILL_ROOT / "documents" / "contracts" / "repo-bootstrap-schema.yaml"
BUILTIN_PHASES = ["IDLE", "COMPLETE", "BLOCKED"]
PHASE_TO_STATE = {
    "start": "STARTING",
    "plan": "PLANNING",
    "implement": "IMPLEMENTING",
    "deploy": "DEPLOYING",
    "final-audit": "FINAL_AUDITING",
}
LEGACY_SEED_PATHS = (
    ("documents", "harnass-os/documents"),
    ("hooks", "harnass-os/hooks"),
    ("scripts/agent-guard.py", "harnass-os/scripts/agent-guard.py"),
)
IMPLICIT_PHASE_STATES = ("IMPLEMENTING", "DEPLOYING")
EXECUTABLE_SUFFIXES = {
    "harnass-os/hooks/pre-commit",
    "harnass-os/hooks/commit-msg",
    "harnass-os/hooks/pre-push",
    "harnass-os/scripts/agent-guard.py",
    "harnass-os/scripts/orchestrator.py",
    "harnass-os/scripts/executor.py",
    "harnass-os/scripts/harnass.py",
}


def fail(message: str, code: int = 1) -> int:
    print(message, file=sys.stderr)
    return code


def discover_registered_phases() -> list[str]:
    """Read suite.json + each SKILL.md docking.phase to build registered_phases."""
    phases = list(BUILTIN_PHASES)
    suite_file = SUITE_ROOT / "suite.json"
    if not suite_file.is_file():
        phases.extend(sorted(set(PHASE_TO_STATE.values())))
        phases.append("READY_FOR_PLAN")
        phases.append("PLAN_REVIEW")
        return phases

    suite_text = suite_file.read_text(encoding="utf-8")
    discovered: list[str] = []
    for match in re.finditer(r'"source"\s*:\s*"([^"]+)"', suite_text):
        skill_dir = SUITE_ROOT / match.group(1)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue
        phase_match = re.search(r"^\s+phase:\s*(.+?)\s*$", fm_match.group(1), re.MULTILINE)
        if phase_match:
            phase_name = phase_match.group(1).strip()
            state = PHASE_TO_STATE.get(phase_name, phase_name.upper().replace("-", "_"))
            if state not in discovered:
                discovered.append(state)

    if not discovered:
        discovered = sorted(set(PHASE_TO_STATE.values()))

    # Insert READY_FOR_PLAN after STARTING if present, and PLAN_REVIEW after PLANNING
    result: list[str] = list(BUILTIN_PHASES)
    for state in discovered:
        if state not in result:
            result.append(state)
    for implicit_state in IMPLICIT_PHASE_STATES:
        if implicit_state not in result:
            result.append(implicit_state)
    for extra in ("READY_FOR_PLAN", "PLAN_REVIEW"):
        if extra not in result:
            result.append(extra)
    return result


def parse_scalar(raw: str) -> str:
    value = raw.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def parse_bootstrap_schema(path: Path) -> dict[str, object]:
    data: dict[str, object] = {"dirs": []}
    in_dirs = False
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s{2}(spec_version|canonical_source|template_manifest):\s*(.+?)\s*$", line)
        if match:
            data[match.group(1)] = parse_scalar(match.group(2))
            in_dirs = False
            continue
        match = re.match(r"^(bootstrap_engine|default_overwrite_policy|default_report_path):\s*(.+?)\s*$", line)
        if match:
            data[match.group(1)] = parse_scalar(match.group(2))
            in_dirs = False
            continue
        if line.strip() == "dirs:":
            in_dirs = True
            continue
        if in_dirs:
            match = re.match(r"^\s{2}-\s*(.+?)\s*$", line)
            if match:
                dirs = data["dirs"]
                assert isinstance(dirs, list)
                dirs.append(parse_scalar(match.group(1)))
                continue
            if line and not line.startswith(" "):
                in_dirs = False
    return data


def parse_manifest(path: Path) -> dict[str, object]:
    manifest: dict[str, object] = {"templates": []}
    in_templates = False
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.strip() == "templates:":
            in_templates = True
            current = None
            continue
        if line.startswith("scaffold_order:"):
            break
        match = re.match(r"^\s{2}spec_version:\s*(.+?)\s*$", line)
        if match:
            manifest["spec_version"] = parse_scalar(match.group(1))
            continue
        if not in_templates:
            continue
        match = re.match(r"^\s{2}-\s+output:\s*(.+?)\s*$", line)
        if match:
            current = {"output": parse_scalar(match.group(1))}
            manifest["templates"].append(current)
            continue
        if current is None:
            continue
        match = re.match(r"^\s{4}([A-Za-z_]+):\s*(.+?)\s*$", line)
        if match:
            current[match.group(1)] = parse_scalar(match.group(2))
    return manifest


def detect_mode(target_root: Path) -> str:
    if not target_root.exists():
        return "greenfield"
    entries = [entry for entry in target_root.iterdir() if entry.name not in {".git", ".gitignore"}]
    if not entries:
        return "greenfield"
    return "retrofit"


def marker_pair(name: str) -> tuple[str, str]:
    begin = f"<!-- BEGIN HARNASS-ENGINEER START MANAGED {name} -->"
    end = f"<!-- END HARNASS-ENGINEER START MANAGED {name} -->"
    return begin, end


def managed_block(name: str, template_text: str) -> str:
    begin, end = marker_pair(name)
    body = template_text.rstrip() + "\n"
    return f"{begin}\n{body}{end}\n"


def replace_or_merge_block(existing: str, name: str, template_text: str) -> tuple[str, str]:
    begin, end = marker_pair(name)
    block = managed_block(name, template_text)
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.DOTALL)
    if pattern.search(existing):
        return pattern.sub(block, existing, count=1), "updated"
    if not existing.strip():
        return block, "created"
    separator = "\n\n" if not existing.endswith("\n") else "\n"
    return existing.rstrip() + separator + block, "merged"


def write_owned_file(dest: Path, template_text: str, overwrite_policy: str) -> str:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(template_text, encoding="utf-8")
        return "created"
    if overwrite_policy == "create-only":
        return "skipped"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(template_text, encoding="utf-8")
    return "updated"


def write_merge_block_file(dest: Path, marker: str, template_text: str, overwrite_policy: str) -> str:
    if overwrite_policy == "force-replace":
        existed = dest.exists()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(managed_block(marker, template_text), encoding="utf-8")
        return "updated" if existed else "created"
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(managed_block(marker, template_text), encoding="utf-8")
        return "created"
    if overwrite_policy == "create-only":
        return "skipped"
    existing = dest.read_text(encoding="utf-8")
    updated, action = replace_or_merge_block(existing, marker, template_text)
    dest.write_text(updated, encoding="utf-8")
    return action


def dump_yaml(value: object, indent: int = 0) -> str:
    space = "  " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                lines.append(f"{space}{key}:")
                lines.append(dump_yaml(child, indent + 1))
            else:
                lines.append(f"{space}{key}: {child}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{space}-")
                lines.append(dump_yaml(item, indent + 1))
            elif isinstance(item, list):
                lines.append(f"{space}-")
                lines.append(dump_yaml(item, indent + 1))
            else:
                lines.append(f"{space}- {item}")
        return "\n".join(lines)
    return f"{space}{value}"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def try_make_executable(path: Path) -> None:
    try:
        path.chmod(path.stat().st_mode | 0o111)
    except OSError:
        return


def ensure_git_repo_and_hooks(target_root: Path) -> int:
    git_dir = subprocess.run(
        ["git", "-C", str(target_root), "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    if git_dir.returncode != 0:
        init = subprocess.run(
            ["git", "init", str(target_root)],
            capture_output=True,
            text=True,
            check=False,
        )
        if init.returncode != 0:
            return fail(
                "bootstrap validation failed: unable to initialize git repository\n" + init.stdout + init.stderr, 1
            )

    hooks = subprocess.run(
        ["git", "-C", str(target_root), "config", "core.hooksPath", "harnass-os/hooks"],
        capture_output=True,
        text=True,
        check=False,
    )
    if hooks.returncode != 0:
        return fail(
            "bootstrap validation failed: unable to configure core.hooksPath\n" + hooks.stdout + hooks.stderr, 1
        )
    return 0


def ensure_directories(target_root: Path, relative_dirs: list[str]) -> list[str]:
    created: list[str] = []
    for relative_dir in relative_dirs:
        path = target_root / relative_dir
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(relative_dir)
    return created


def seed_harnass_os_from_legacy(target_root: Path) -> set[str]:
    seeded_outputs: set[str] = set()
    for legacy_rel, canonical_rel in LEGACY_SEED_PATHS:
        legacy_path = target_root / legacy_rel
        if not legacy_path.exists():
            continue
        canonical_path = target_root / canonical_rel
        if legacy_path.is_dir():
            for source in legacy_path.rglob("*"):
                destination = canonical_path / source.relative_to(legacy_path)
                if source.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    continue
                shutil.copy2(source, destination)
                if legacy_rel == "documents":
                    seeded_outputs.add(destination.relative_to(target_root).as_posix())
            continue
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        if not canonical_path.exists():
            shutil.copy2(legacy_path, canonical_path)
            seeded_outputs.add(canonical_path.relative_to(target_root).as_posix())
    return seeded_outputs


def materialize(
    target_root: Path,
    manifest_path: Path,
    overwrite_policy: str,
    report_path: Path,
    mode: str,
    spec_version: str,
    required_dirs: list[str],
    protected_outputs: set[str] | None = None,
) -> dict[str, object]:
    manifest = parse_manifest(manifest_path)
    templates = manifest["templates"]
    protected_outputs = protected_outputs or set()
    report: dict[str, object] = {
        "bootstrap": {
            "mode": mode,
            "overwrite_policy": overwrite_policy,
            "spec_version": spec_version or manifest.get("spec_version", "unknown"),
            "target_root": str(target_root),
        },
        "created": [],
        "updated": [],
        "merged": [],
        "skipped": [],
        "created_dirs": [],
        "missing_outputs": [],
        "missing_directories": [],
    }

    created_dirs = ensure_directories(target_root, required_dirs)
    report["created_dirs"] = created_dirs

    for entry in templates:
        assert isinstance(entry, dict)
        output = entry["output"]
        template = entry["template"]
        write_mode = entry.get("write_mode", "replace_owned")
        marker = entry.get("managed_marker", output.replace("/", "::"))
        dest = target_root / output
        template_path = manifest_path.parent / template
        template_text = template_path.read_text(encoding="utf-8")

        if write_mode == "merge_block":
            action = write_merge_block_file(dest, marker, template_text, overwrite_policy)
        elif output in protected_outputs and overwrite_policy == "create-or-merge":
            action = "skipped"
        else:
            action = write_owned_file(dest, template_text, overwrite_policy)

        cast = report[action]
        assert isinstance(cast, list)
        cast.append(output)
        if output in EXECUTABLE_SUFFIXES:
            try_make_executable(dest)

    for entry in templates:
        assert isinstance(entry, dict)
        output = entry["output"]
        if not (target_root / output).exists():
            missing = report["missing_outputs"]
            assert isinstance(missing, list)
            missing.append(output)

    for relative_dir in required_dirs:
        if not (target_root / relative_dir).is_dir():
            missing = report["missing_directories"]
            assert isinstance(missing, list)
            missing.append(relative_dir)

    ensure_parent(report_path)
    report_path.write_text(dump_yaml(report) + "\n", encoding="utf-8")
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_repo_root", help="Target repository root to scaffold")
    parser.add_argument("--mode", choices=("auto", "greenfield", "retrofit"), default="auto")
    parser.add_argument(
        "--overwrite-policy",
        choices=("create-or-merge", "create-only", "force-replace"),
        default="create-or-merge",
    )
    parser.add_argument("--report", help="Override the bootstrap report output path")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv[1:])
    schema_data = parse_bootstrap_schema(BOOTSTRAP_SCHEMA)
    manifest_rel = schema_data.get("template_manifest")
    if not manifest_rel:
        return fail("repo-bootstrap-schema.yaml must define template_manifest", 2)

    manifest_path = (BOOTSTRAP_SCHEMA.parent / str(manifest_rel)).resolve()
    if not manifest_path.is_file():
        return fail(f"template manifest not found: {manifest_path}", 2)

    target_root = Path(args.target_repo_root).resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    mode = args.mode if args.mode != "auto" else detect_mode(target_root)
    protected_outputs: set[str] = set()
    if mode == "retrofit":
        protected_outputs = seed_harnass_os_from_legacy(target_root)
    default_report_rel = str(
        schema_data.get("default_report_path", f"harnass-os/documents/runs/history/bootstrap-{mode}.yaml")
    )
    default_report_rel = default_report_rel.replace("<mode>", mode)
    report_path = (target_root / args.report).resolve() if args.report else (target_root / default_report_rel).resolve()
    required_dirs = [str(item) for item in schema_data.get("dirs", [])]

    report = materialize(
        target_root=target_root,
        manifest_path=manifest_path,
        overwrite_policy=args.overwrite_policy,
        report_path=report_path,
        mode=mode,
        spec_version=str(schema_data.get("spec_version", "unknown")),
        required_dirs=required_dirs,
        protected_outputs=protected_outputs,
    )

    # Fill version stamp and initialize orchestrator state.
    version_file = target_root / "harnass-os" / "documents" / ".harnass-version.yaml"
    orchestrator_file = target_root / "harnass-os" / "documents" / "orchestrator" / "current.yaml"
    if version_file.is_file():
        from datetime import UTC, datetime

        stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        text = version_file.read_text(encoding="utf-8")
        text = re.sub(r"bootstrapped_at:.*", f"bootstrapped_at: {stamp}", text)
        version_file.write_text(text, encoding="utf-8")
        if orchestrator_file.is_file():
            orchestrator_text = orchestrator_file.read_text(encoding="utf-8")
            # Write dynamically discovered registered_phases
            phases = discover_registered_phases()
            phases_yaml = "registered_phases:\n" + "\n".join(f"  - {p}" for p in phases)
            orchestrator_text = re.sub(
                r"^registered_phases:.*?(?=\n\S)",
                phases_yaml + "\n",
                orchestrator_text,
                flags=re.MULTILINE | re.DOTALL,
            )
            orchestrator_text = re.sub(r"^state:.*$", "state: READY_FOR_PLAN", orchestrator_text, flags=re.MULTILINE)
            orchestrator_text = re.sub(
                r"^previous_stable_state:.*$",
                "previous_stable_state: READY_FOR_PLAN",
                orchestrator_text,
                flags=re.MULTILINE,
            )
            orchestrator_text = re.sub(
                r"^last_transition:.*$",
                "last_transition: scaffold-ready",
                orchestrator_text,
                flags=re.MULTILINE,
            )
            orchestrator_text = re.sub(
                r"^updated_at:.*$", f"updated_at: {stamp}", orchestrator_text, flags=re.MULTILINE
            )
            orchestrator_file.write_text(orchestrator_text, encoding="utf-8")

    git_result = ensure_git_repo_and_hooks(target_root)
    if git_result != 0:
        return git_result

    print(dump_yaml(report))
    missing_outputs = report["missing_outputs"]
    assert isinstance(missing_outputs, list)
    missing_directories = report["missing_directories"]
    assert isinstance(missing_directories, list)
    if missing_outputs or missing_directories:
        return fail("bootstrap validation failed: scaffold is incomplete after materialization", 1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
