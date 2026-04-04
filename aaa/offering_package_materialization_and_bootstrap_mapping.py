import json
from pathlib import Path
from typing import Any


ALLOWED_PACKAGE_LEVELS = {"lite", "core", "full"}
ALLOWED_REPO_IDS = {
    ".github",
    "aaa-actions",
    "aaa-evals",
    "aaa-tools",
    "aaa-prompts",
    "aaa-tpl-docs",
    "aaa-tpl-service",
    "aaa-tpl-frontend",
}
ALLOWED_WORKFLOW_LEVELS = {"reduced", "core", "full"}
ALLOWED_GOVERNANCE_ASSETS = {
    "ai_command_center",
    "project_playbook",
    "operate_maintain_workflow_v2_reduced",
    "operate_maintain_workflow_v2_core",
    "operate_maintain_workflow_v2_full",
    "prompts_baseline",
    "evals_baseline",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    minimum_repo_set = bundle.get("minimum_repo_set", [])
    governance_asset_load_list = bundle.get("governance_asset_load_list", [])
    package_level = str(bundle.get("package_level", "")).strip()
    workflow_inclusion_level = str(bundle.get("workflow_inclusion_level", "")).strip()
    mapping_completeness = str(bundle.get("mapping_completeness", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "offering_package_materialization_mapping":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be offering_package_materialization_mapping",
            }
        )
    if bundle.get("line_class") != "offering_package_runtime_enablement_line":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be offering_package_runtime_enablement_line",
            }
        )
    if bundle.get("baseline_scope") != "pre_topology_baseline":
        errors.append(
            {
                "code": "baseline_scope",
                "message": "baseline_scope must be pre_topology_baseline",
            }
        )
    if bundle.get("post_topology_consumption_required") is not True:
        errors.append(
            {
                "code": "post_topology_consumption_required",
                "message": "post_topology_consumption_required must be true",
            }
        )
    if bundle.get("topology_mapping_precedence_ref") != "v2.1.34":
        errors.append(
            {
                "code": "topology_mapping_precedence_ref",
                "message": "topology_mapping_precedence_ref must be v2.1.34",
            }
        )
    if package_level not in ALLOWED_PACKAGE_LEVELS:
        errors.append({"code": "package_level", "message": "package_level is not allowed"})
    if not isinstance(minimum_repo_set, list) or len(minimum_repo_set) < 3:
        errors.append(
            {
                "code": "minimum_repo_set",
                "message": "minimum_repo_set must be a non-empty array with at least 3 repos",
            }
        )
    else:
        unsupported_repos = [repo for repo in minimum_repo_set if str(repo).strip() not in ALLOWED_REPO_IDS]
        if unsupported_repos:
            errors.append(
                {
                    "code": "minimum_repo_set",
                    "message": "minimum_repo_set includes unsupported repo identifiers",
                }
            )
    if workflow_inclusion_level not in ALLOWED_WORKFLOW_LEVELS:
        errors.append(
            {
                "code": "workflow_inclusion_level",
                "message": "workflow_inclusion_level is not allowed",
            }
        )
    if not isinstance(bundle.get("template_sync_required"), bool):
        errors.append(
            {
                "code": "template_sync_required",
                "message": "template_sync_required must be a boolean",
            }
        )
    if not isinstance(bundle.get("workflow_enablement_required"), bool):
        errors.append(
            {
                "code": "workflow_enablement_required",
                "message": "workflow_enablement_required must be a boolean",
            }
        )
    if not isinstance(governance_asset_load_list, list) or not governance_asset_load_list:
        errors.append(
            {
                "code": "governance_asset_load_list",
                "message": "governance_asset_load_list must be a non-empty array",
            }
        )
    else:
        unsupported_assets = [
            asset for asset in governance_asset_load_list if str(asset).strip() not in ALLOWED_GOVERNANCE_ASSETS
        ]
        if unsupported_assets:
            errors.append(
                {
                    "code": "governance_asset_load_list",
                    "message": "governance_asset_load_list includes unsupported asset identifiers",
                }
            )
    if bundle.get("materialization_target_mode") != "repo_template_workflow_asset_mapping":
        errors.append(
            {
                "code": "materialization_target_mode",
                "message": "materialization_target_mode must be repo_template_workflow_asset_mapping",
            }
        )
    if mapping_completeness != "complete":
        errors.append(
            {
                "code": "mapping_completeness",
                "message": "mapping_completeness must be complete",
            }
        )
    if bundle.get("dedicated_github_universal_invariant") is not False:
        errors.append(
            {
                "code": "dedicated_github_universal_invariant",
                "message": "dedicated_github_universal_invariant must be false",
            }
        )
    if bundle.get("package_status_assertion_included") is not False:
        errors.append(
            {
                "code": "package_status_assertion_included",
                "message": "package_status_assertion_included must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "offering_package_materialization_mapping",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "package_level": package_level,
            "minimum_repo_set": minimum_repo_set,
            "workflow_inclusion_level": workflow_inclusion_level,
            "template_sync_required": bundle.get("template_sync_required"),
            "workflow_enablement_required": bundle.get("workflow_enablement_required"),
            "governance_asset_load_list": governance_asset_load_list,
            "topology_mapping_precedence_ref": bundle.get("topology_mapping_precedence_ref"),
            "post_topology_consumption_required": bundle.get("post_topology_consumption_required"),
            "materialization_target_mode": bundle.get("materialization_target_mode"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
