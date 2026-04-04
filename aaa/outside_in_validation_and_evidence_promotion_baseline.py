import hashlib
import json
from pathlib import Path
from typing import Any

from . import package_commands


FIXED_REPORT_SECTIONS: dict[str, str] = {
    "execution_steps": "Step-by-step log",
    "observed_outputs": "Observed outputs",
    "topology_assumption_summary": "Topology assumption summary",
    "blockers": "Blockers",
    "evidence_to_preserve": "What evidence should be preserved outside /tmp",
    "follow_up_tests": "Suggested follow-up tests",
}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _assert_tmp_workspace(workspace_root: Path) -> Path:
    resolved = workspace_root.resolve()
    resolved_str = str(resolved)
    if resolved_str != "/tmp" and not resolved_str.startswith("/tmp/") and resolved_str != "/private/tmp" and not resolved_str.startswith("/private/tmp/"):
        raise ValueError("outside-in validation workspace must live under /tmp")
    return resolved


def build_baseline_bundle() -> dict[str, Any]:
    return {
        "version": "v0.1",
        "runtime_plane_mode": "outside_in_validation_and_evidence_promotion_baseline",
        "line_class": "outside_in_follow_up_line",
        "validation_mode": "outside_in_remote_client",
        "disposable_workspace_class": "tmp_sandbox",
        "canonical_evidence_plane": "aaa_tpl_docs_canonical_evidence",
        "canonical_evidence_plane_is_disposable": False,
        "explicit_promotion_required": True,
        "fixed_report_sections": list(FIXED_REPORT_SECTIONS.keys()),
        "comparison_ready_result_bundle": True,
        "promotion_candidate_manifest": True,
        "prose_fallback_allowed": False,
    }


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "version must be v0.1"})
    if bundle.get("runtime_plane_mode") != "outside_in_validation_and_evidence_promotion_baseline":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be outside_in_validation_and_evidence_promotion_baseline",
            }
        )
    if bundle.get("validation_mode") != "outside_in_remote_client":
        errors.append({"code": "validation_mode", "message": "validation_mode must be outside_in_remote_client"})
    if bundle.get("disposable_workspace_class") != "tmp_sandbox":
        errors.append({"code": "disposable_workspace_class", "message": "disposable_workspace_class must be tmp_sandbox"})
    if bundle.get("canonical_evidence_plane") != "aaa_tpl_docs_canonical_evidence":
        errors.append(
            {"code": "canonical_evidence_plane", "message": "canonical_evidence_plane must be aaa_tpl_docs_canonical_evidence"}
        )
    if bundle.get("canonical_evidence_plane_is_disposable") is not False:
        errors.append(
            {
                "code": "canonical_evidence_plane_is_disposable",
                "message": "canonical_evidence_plane_is_disposable must be false",
            }
        )
    if bundle.get("explicit_promotion_required") is not True:
        errors.append(
            {"code": "explicit_promotion_required", "message": "explicit_promotion_required must be true"}
        )
    if bundle.get("comparison_ready_result_bundle") is not True:
        errors.append(
            {
                "code": "comparison_ready_result_bundle",
                "message": "comparison_ready_result_bundle must be true",
            }
        )
    if bundle.get("promotion_candidate_manifest") is not True:
        errors.append(
            {"code": "promotion_candidate_manifest", "message": "promotion_candidate_manifest must be true"}
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    required_sections = set(FIXED_REPORT_SECTIONS.keys())
    actual_sections = set(bundle.get("fixed_report_sections", []))
    if actual_sections != required_sections:
        errors.append(
            {
                "code": "fixed_report_sections",
                "message": "fixed_report_sections must exactly match the canonical outside-in report section set",
            }
        )

    return {
        "ok": not errors,
        "errors": errors,
        "derived_results": {
            "explicit_promotion_required": True,
            "canonical_evidence_plane_is_disposable": False,
            "fixed_report_sections_count": len(FIXED_REPORT_SECTIONS),
        },
    }


def _split_sections(note_text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None
    for raw_line in note_text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith("## "):
            current_heading = line[3:].strip()
            sections[current_heading] = []
            continue
        if current_heading is not None:
            sections[current_heading].append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def _parse_bullet_items(section_text: str) -> list[str]:
    items: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip().strip("`"))
    return items


def _candidate_manifest(workspace_root: Path, note_sections: dict[str, str], note_path: Path) -> dict[str, Any]:
    preserve_section = note_sections.get(FIXED_REPORT_SECTIONS["evidence_to_preserve"], "")
    requested_paths = _parse_bullet_items(preserve_section)
    candidate_artifacts: list[dict[str, Any]] = []

    for raw_path in requested_paths:
        artifact_path = Path(raw_path)
        resolved = artifact_path if artifact_path.is_absolute() else workspace_root / artifact_path
        candidate_artifacts.append(
            {
                "artifact_path": str(resolved),
                "declared_path": raw_path,
                "exists": resolved.exists(),
                "workspace_scoped": str(resolved).startswith(str(workspace_root)),
                "requires_explicit_promotion": True,
                "canonical_reference_allowed": False,
            }
        )

    init_report_path = workspace_root / "aaa-init-report.json"
    if init_report_path.exists():
        candidate_artifacts.append(
            {
                "artifact_path": str(init_report_path),
                "declared_path": "aaa-init-report.json",
                "exists": True,
                "workspace_scoped": True,
                "requires_explicit_promotion": True,
                "canonical_reference_allowed": False,
            }
        )

    local_bundle_path = workspace_root / ".aaa" / "local_sandbox_bootstrap_candidate_evidence.json"
    if local_bundle_path.exists():
        candidate_artifacts.append(
            {
                "artifact_path": str(local_bundle_path),
                "declared_path": ".aaa/local_sandbox_bootstrap_candidate_evidence.json",
                "exists": True,
                "workspace_scoped": True,
                "requires_explicit_promotion": True,
                "canonical_reference_allowed": False,
            }
        )

    return {
        "manifest_version": "v0.1",
        "workspace_root": str(workspace_root),
        "validation_note_path": str(note_path.resolve()),
        "explicit_promotion_required": True,
        "canonical_evidence_plane": "aaa_tpl_docs_canonical_evidence",
        "disposable_workspace_output_is_canonical": False,
        "unpromoted_artifacts_citable_by_version_index": False,
        "unpromoted_artifacts_citable_by_completion_evidence": False,
        "unpromoted_artifacts_citable_by_canonical_registry": False,
        "unpromoted_artifacts_citable_by_downstream_comparison_bundle": False,
        "candidate_artifacts": candidate_artifacts,
    }


def run_validation(note_path: str | Path, workspace: str | Path, level: str, topology_mode: str) -> dict[str, Any]:
    note_file = Path(note_path).resolve()
    if not note_file.is_file():
        raise FileNotFoundError(f"outside-in validation note does not exist: {note_file}")
    workspace_root = _assert_tmp_workspace(Path(workspace))

    bundle = build_baseline_bundle()
    baseline_validation = validate_bundle(bundle)
    note_text = note_file.read_text(encoding="utf-8")
    note_sections = _split_sections(note_text)

    missing_sections = [
        section_id
        for section_id, heading in FIXED_REPORT_SECTIONS.items()
        if heading not in note_sections or not note_sections[heading]
    ]
    if missing_sections:
        raise ValueError("outside-in validation note is missing required sections: " + ",".join(missing_sections))

    package_status = package_commands.status(level, topology_mode, workspace_root)
    manifest = _candidate_manifest(workspace_root, note_sections, note_file)

    report = {
        "note_path": str(note_file),
        "workspace_root": str(workspace_root),
        "sections_present": list(FIXED_REPORT_SECTIONS.keys()),
        "section_heading_map": FIXED_REPORT_SECTIONS,
        "section_digest": _sha256_text("\n".join(f"{k}:{FIXED_REPORT_SECTIONS[k]}" for k in FIXED_REPORT_SECTIONS)),
        "missing_sections": [],
        "note_digest_sha256": _sha256_text(note_text),
    }

    comparison_ready_result_bundle = {
        "bundle_version": "v0.1",
        "validation_mode": "outside_in_remote_client",
        "package_level": level,
        "topology_mode_expected": package_status["topology_status"]["topology_mode_expected"],
        "topology_mode_detected": package_status["topology_status"]["topology_mode_detected"],
        "topology_mode_resolved": package_status["topology_status"]["topology_mode_resolved"],
        "structure_acceptance_status": package_status["topology_status"]["structure_acceptance_status"],
        "topology_completion_status": package_status["topology_status"]["topology_completion_status"],
        "explicit_promotion_required": True,
        "disposable_workspace_output_is_canonical": False,
        "validation_note_digest_sha256": report["note_digest_sha256"],
    }

    return {
        "command": "outside_in_validate",
        "baseline_bundle": bundle,
        "validation": baseline_validation,
        "report": report,
        "topology_assumption_summary": {
            "package_level": level,
            "topology_mode_expected": package_status["topology_status"]["topology_mode_expected"],
            "topology_mode_detected": package_status["topology_status"]["topology_mode_detected"],
            "topology_mode_resolved": package_status["topology_status"]["topology_mode_resolved"],
        },
        "promotion_candidate_manifest": manifest,
        "comparison_ready_result_bundle": comparison_ready_result_bundle,
    }


def render_payload(payload: dict[str, Any], output_format: str) -> str:
    if output_format in {"json", "llm"}:
        return json.dumps(payload, indent=2, ensure_ascii=True)

    comparison = payload["comparison_ready_result_bundle"]
    manifest = payload["promotion_candidate_manifest"]
    lines = [
        "command=outside_in_validate",
        f"package_level={comparison['package_level']}",
        f"topology_expected={comparison['topology_mode_expected']}",
        f"topology_detected={comparison['topology_mode_detected']}",
        f"topology_resolved={comparison['topology_mode_resolved']}",
        f"structure_acceptance_status={comparison['structure_acceptance_status']}",
        f"topology_completion_status={comparison['topology_completion_status']}",
        f"explicit_promotion_required={str(manifest['explicit_promotion_required']).lower()}",
        f"candidate_artifact_count={len(manifest['candidate_artifacts'])}",
    ]
    return "\n".join(lines)
