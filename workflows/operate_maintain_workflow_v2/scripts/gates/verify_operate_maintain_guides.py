#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+")
STEP_RE = re.compile(r"^###\s+Step\s+([1-4])")
CHECKLIST_RE = re.compile(r"^####\s+Step\s+([1-4])\s+Exit\s+Checklist")
ENUM_RE = re.compile(r"^-\s+`([^`]+)`")


@dataclass
class GuideSummary:
    sections: List[str]
    steps: List[str]
    checklist_versions: Dict[str, str]
    enums: List[str]
    has_version_index_ref: bool
    has_workflow_index_ref: bool


def _parse_markdown(path: Path) -> GuideSummary:
    lines = path.read_text(encoding="utf-8").splitlines()

    sections: List[str] = []
    steps: List[str] = []
    checklist_versions: Dict[str, str] = {}
    enums: List[str] = []

    has_version_index_ref = False
    has_workflow_index_ref = False

    in_yaml = False
    pending_checklist_step: str | None = None

    for line in lines:
        if "aaa-tpl-docs/ops/index/version_index.md" in line:
            has_version_index_ref = True
        if "aaa-tpl-docs/ops/index/workflow_index.md" in line:
            has_workflow_index_ref = True

        m = SECTION_RE.match(line)
        if m:
            sections.append(m.group(1))

        m = STEP_RE.match(line)
        if m:
            steps.append(m.group(1))

        m = CHECKLIST_RE.match(line)
        if m:
            pending_checklist_step = m.group(1)

        if line.strip() == "```yaml" and pending_checklist_step:
            in_yaml = True
            continue

        if in_yaml and line.strip() == "```":
            in_yaml = False
            pending_checklist_step = None
            continue

        if in_yaml and pending_checklist_step and line.strip().startswith("ExitChecklistVersion:"):
            checklist_versions[pending_checklist_step] = line.split(":", 1)[1].strip()

    in_enum_section = False
    for line in lines:
        if line.startswith("## 7."):
            in_enum_section = True
            continue
        if in_enum_section and line.startswith("## "):
            in_enum_section = False
        if in_enum_section:
            m = ENUM_RE.match(line.strip())
            if m:
                enums.append(m.group(1))

    return GuideSummary(
        sections=sections,
        steps=steps,
        checklist_versions=checklist_versions,
        enums=enums,
        has_version_index_ref=has_version_index_ref,
        has_workflow_index_ref=has_workflow_index_ref,
    )


def _compare(core: GuideSummary, tpl: GuideSummary) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    required_sections = [str(i) for i in range(0, 9)]
    for sec in required_sections:
        if sec not in core.sections:
            errors.append(f"core missing section {sec}")
        if sec not in tpl.sections:
            errors.append(f"template missing section {sec}")

    for step in ["1", "2", "3", "4"]:
        if step not in core.steps:
            errors.append(f"core missing Step {step}")
        if step not in tpl.steps:
            errors.append(f"template missing Step {step}")
        c_ver = core.checklist_versions.get(step)
        t_ver = tpl.checklist_versions.get(step)
        if not c_ver or not t_ver:
            errors.append(f"missing checklist version for Step {step}")
        elif c_ver != t_ver:
            errors.append(f"Step {step} checklist version mismatch: core={c_ver}, tpl={t_ver}")

    if sorted(core.enums) != sorted(tpl.enums):
        errors.append("canonical enums mismatch between core and template")

    if not tpl.has_version_index_ref:
        errors.append("template guide missing aaa-tpl-docs/ops/index/version_index.md reference")
    if not tpl.has_workflow_index_ref:
        errors.append("template guide missing aaa-tpl-docs/ops/index/workflow_index.md reference")

    return (len(errors) == 0, errors)


def _autofix_copy_core(core_path: Path, tpl_path: Path) -> None:
    tpl_path.write_text(core_path.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify operate_maintain_guide parity (v2.1.0 gate)")
    parser.add_argument("--core-guide", required=True)
    parser.add_argument("--tpl-guide", required=True)
    parser.add_argument("--report", required=False)
    parser.add_argument("--autofix-copy-core", action="store_true")
    args = parser.parse_args()

    core_path = Path(args.core_guide)
    tpl_path = Path(args.tpl_guide)

    if args.autofix_copy_core:
        _autofix_copy_core(core_path, tpl_path)

    core = _parse_markdown(core_path)
    tpl = _parse_markdown(tpl_path)
    ok, errors = _compare(core, tpl)

    payload = {
        "gate": "operate_maintain_guide_parity_v2_0_1",
        "core_guide": str(core_path),
        "tpl_guide": str(tpl_path),
        "ok": ok,
        "errors": errors,
    }

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
