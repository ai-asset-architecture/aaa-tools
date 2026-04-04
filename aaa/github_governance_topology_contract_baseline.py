import json
from pathlib import Path
from typing import Any


ALLOWED_TOPOLOGY_MODE = {"dedicated_repo", "repo_local", "hybrid"}
ALLOWED_AUTHORITY_SPLIT = {"org_centralized", "repo_distributed", "mixed_authority"}
ALLOWED_ASSET_CLASS = {
    "org_profile_metadata",
    "issue_template_assets",
    "pull_request_template_assets",
    "org_level_governance_docs",
    "reusable_workflow_carriers",
    "repo_local_workflows",
    "codeowners",
    "branch_protection_binding",
    "governance_policy_refs",
}
ALLOWED_PLACEMENT_MODE = {"org_repo_only", "repo_local_only", "hybrid_split"}
ALLOWED_PRECEDENCE_RULE = {"org_precedence", "repo_precedence", "single_source_only"}
ALLOWED_CONFLICT_RULE = {"hard_fail", "degraded", "not_evaluable"}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    topology_mode = str(bundle.get("topology_mode", "")).strip()
    authority_split = str(bundle.get("authority_split", "")).strip()
    asset_model = bundle.get("asset_class_authority_model", [])

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "github_governance_topology_contract_baseline":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be github_governance_topology_contract_baseline",
            }
        )
    if bundle.get("line_class") != "github_governance_topology_support_program":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be github_governance_topology_support_program",
            }
        )
    if topology_mode not in ALLOWED_TOPOLOGY_MODE:
        errors.append({"code": "topology_mode", "message": "topology_mode is not allowed"})
    if authority_split not in ALLOWED_AUTHORITY_SPLIT:
        errors.append({"code": "authority_split", "message": "authority_split is not allowed"})
    if bundle.get("precedence_law") != "machine_checkable_precedence_required":
        errors.append({"code": "precedence_law", "message": "precedence_law must be machine_checkable_precedence_required"})
    if bundle.get("conflict_law") != "machine_checkable_conflict_verdict_required":
        errors.append({"code": "conflict_law", "message": "conflict_law must be machine_checkable_conflict_verdict_required"})
    if bundle.get("evidence_sufficiency_law") != "machine_checkable_evidence_sufficiency_required":
        errors.append(
            {
                "code": "evidence_sufficiency_law",
                "message": "evidence_sufficiency_law must be machine_checkable_evidence_sufficiency_required",
            }
        )
    if bundle.get("dedicated_repo_existence_is_only_truth") is not False:
        errors.append(
            {
                "code": "dedicated_repo_existence_is_only_truth",
                "message": "dedicated_repo_existence_is_only_truth must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    if not isinstance(asset_model, list) or len(asset_model) < 3:
        errors.append(
            {
                "code": "asset_class_authority_model",
                "message": "asset_class_authority_model must contain at least three asset classes",
            }
        )
    else:
        seen_asset_classes: set[str] = set()
        for item in asset_model:
            if not isinstance(item, dict):
                errors.append({"code": "asset_class_authority_model", "message": "asset model entries must be objects"})
                break
            asset_class = str(item.get("asset_class", "")).strip()
            allowed_topology_modes = item.get("allowed_topology_modes", [])
            authority_owner = str(item.get("authority_owner", "")).strip()
            placement_mode = str(item.get("placement_mode", "")).strip()
            precedence_rule = str(item.get("precedence_rule", "")).strip()
            conflict_rule = str(item.get("conflict_rule", "")).strip()
            evidence_requirements = item.get("evidence_requirements", [])

            if asset_class not in ALLOWED_ASSET_CLASS:
                errors.append({"code": "asset_class", "message": "asset_class is not allowed"})
                continue
            seen_asset_classes.add(asset_class)
            if not isinstance(allowed_topology_modes, list) or not allowed_topology_modes:
                errors.append({"code": "allowed_topology_modes", "message": "allowed_topology_modes must be a non-empty array"})
            elif any(str(mode).strip() not in ALLOWED_TOPOLOGY_MODE for mode in allowed_topology_modes):
                errors.append({"code": "allowed_topology_modes", "message": "allowed_topology_modes includes an unsupported topology"})
            if authority_owner not in ALLOWED_AUTHORITY_SPLIT:
                errors.append({"code": "authority_owner", "message": "authority_owner is not allowed"})
            if placement_mode not in ALLOWED_PLACEMENT_MODE:
                errors.append({"code": "placement_mode", "message": "placement_mode is not allowed"})
            if precedence_rule not in ALLOWED_PRECEDENCE_RULE:
                errors.append({"code": "precedence_rule", "message": "precedence_rule is not allowed"})
            if conflict_rule not in ALLOWED_CONFLICT_RULE:
                errors.append({"code": "conflict_rule", "message": "conflict_rule is not allowed"})
            if not isinstance(evidence_requirements, list) or not evidence_requirements:
                errors.append({"code": "evidence_requirements", "message": "evidence_requirements must be a non-empty array"})

        if topology_mode == "hybrid":
            if "org_profile_metadata" not in seen_asset_classes:
                errors.append(
                    {
                        "code": "asset_class_authority_model",
                        "message": "hybrid must include org_profile_metadata authority modeling",
                    }
                )
            if "repo_local_workflows" not in seen_asset_classes:
                errors.append(
                    {
                        "code": "asset_class_authority_model",
                        "message": "hybrid must include repo_local_workflows authority modeling",
                    }
                )
            if "codeowners" not in seen_asset_classes:
                errors.append(
                    {
                        "code": "asset_class_authority_model",
                        "message": "hybrid must include codeowners authority modeling",
                    }
                )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "github_governance_topology_contract_baseline",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "topology_mode": topology_mode,
            "authority_split": authority_split,
            "asset_class_count": len(asset_model) if isinstance(asset_model, list) else 0,
            "precedence_law": bundle.get("precedence_law"),
            "conflict_law": bundle.get("conflict_law"),
            "evidence_sufficiency_law": bundle.get("evidence_sufficiency_law"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
