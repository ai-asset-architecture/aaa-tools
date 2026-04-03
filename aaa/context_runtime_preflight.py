import json
from pathlib import Path
from typing import Any


ALLOWED_CURRENT_TRUTH_SOURCES = {
    "canonical_contract_docs",
    "canonical_registries_indexes",
    "preserved_completion_audit_artifacts",
    "repo_tracked_files",
}

ALLOWED_SUPPORTING_SOURCES = {
    "external_execution_outputs",
    "local_operation_logs",
    "generated_runtime_summaries",
}

ALLOWED_PREFLIGHT_CHECKS = {
    "current_truth_source_check",
    "supporting_source_check",
    "anti_contamination_check",
    "promotion_block_check",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    current_truth_sources = [str(item).strip() for item in bundle.get("current_truth_sources", [])]
    supporting_sources = [str(item).strip() for item in bundle.get("supporting_sources", [])]
    preflight_checks = [str(item).strip() for item in bundle.get("preflight_checks", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})

    bundle_id = str(bundle.get("bundle_id", "")).strip()
    if not bundle_id:
        errors.append({"code": "bundle_id", "message": "bundle_id is required"})

    unknown_current_truth_sources = [
        item for item in current_truth_sources if item not in ALLOWED_CURRENT_TRUTH_SOURCES
    ]
    if unknown_current_truth_sources:
        errors.append(
            {
                "code": "current_truth_sources",
                "message": f"unknown or disallowed current truth sources: {', '.join(unknown_current_truth_sources)}",
            }
        )

    unknown_supporting_sources = [item for item in supporting_sources if item not in ALLOWED_SUPPORTING_SOURCES]
    if unknown_supporting_sources:
        errors.append(
            {
                "code": "supporting_sources",
                "message": f"unknown supporting sources: {', '.join(unknown_supporting_sources)}",
            }
        )

    unknown_preflight_checks = [item for item in preflight_checks if item not in ALLOWED_PREFLIGHT_CHECKS]
    if unknown_preflight_checks:
        errors.append(
            {
                "code": "preflight_checks",
                "message": f"unknown preflight checks: {', '.join(unknown_preflight_checks)}",
            }
        )

    if "local_operation_logs" in current_truth_sources:
        errors.append(
            {
                "code": "current_truth_sources",
                "message": "local_operation_logs cannot be promoted to current truth",
            }
        )

    required_preflight_checks = {
        "current_truth_source_check",
        "supporting_source_check",
        "anti_contamination_check",
        "promotion_block_check",
    }
    missing_preflight_checks = [item for item in required_preflight_checks if item not in preflight_checks]
    if missing_preflight_checks:
        errors.append(
            {
                "code": "preflight_checks",
                "message": f"missing required preflight checks: {', '.join(sorted(missing_preflight_checks))}",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "bundle_id": bundle_id,
        "resolved_current_truth_sources": current_truth_sources,
        "resolved_supporting_sources": supporting_sources,
        "resolved_preflight_checks": preflight_checks,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    bundle = load_bundle(bundle_path)
    result = validate_bundle(bundle)
    result["bundle_path"] = str(Path(bundle_path))
    return result
