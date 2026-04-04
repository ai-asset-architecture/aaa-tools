import json
from pathlib import Path
from typing import Any


ALLOWED_PACKAGE_LEVEL = {"lite", "core", "full"}
ALLOWED_TOPOLOGY_MODE = {"dedicated_repo", "repo_local", "hybrid"}
ALLOWED_WORKFLOW_LEVEL = {"reduced", "core", "full"}
ALLOWED_PLACEMENT_RULE = {"org_repo_only", "repo_local_only", "hybrid_split"}
SOURCE_DEFINITION_ARTIFACT_REF = "aaa-docs/bootstrap/offering_definition_skeleton.md"


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    package_level = str(bundle.get("package_level", "")).strip()
    topology_mode = str(bundle.get("topology_mode", "")).strip()
    minimum_repo_set = bundle.get("minimum_repo_set_by_topology", [])
    workflow_level = str(bundle.get("workflow_inclusion_level_by_topology", "")).strip()
    placement_rules = bundle.get("governance_asset_placement_rules", [])
    source_definition_artifact_ref = str(bundle.get("source_definition_artifact_ref", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "topology_aware_offering_package_definition_resolution":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be topology_aware_offering_package_definition_resolution",
            }
        )
    if bundle.get("line_class") != "github_governance_topology_support_program":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be github_governance_topology_support_program",
            }
        )
    if package_level not in ALLOWED_PACKAGE_LEVEL:
        errors.append({"code": "package_level", "message": "package_level is not allowed"})
    if topology_mode not in ALLOWED_TOPOLOGY_MODE:
        errors.append({"code": "topology_mode", "message": "topology_mode is not allowed"})
    if source_definition_artifact_ref != SOURCE_DEFINITION_ARTIFACT_REF:
        errors.append(
            {
                "code": "source_definition_artifact_ref",
                "message": "source_definition_artifact_ref must point to the offering mother draft",
            }
        )
    if not isinstance(minimum_repo_set, list) or not minimum_repo_set:
        errors.append(
            {
                "code": "minimum_repo_set_by_topology",
                "message": "minimum_repo_set_by_topology must be a non-empty array",
            }
        )
    if workflow_level not in ALLOWED_WORKFLOW_LEVEL:
        errors.append(
            {
                "code": "workflow_inclusion_level_by_topology",
                "message": "workflow_inclusion_level_by_topology is not allowed",
            }
        )
    if not isinstance(placement_rules, list) or not placement_rules:
        errors.append(
            {
                "code": "governance_asset_placement_rules",
                "message": "governance_asset_placement_rules must be a non-empty array",
            }
        )
    else:
        for item in placement_rules:
            if str(item).strip() not in ALLOWED_PLACEMENT_RULE:
                errors.append(
                    {
                        "code": "governance_asset_placement_rules",
                        "message": "governance_asset_placement_rules includes an unsupported placement rule",
                    }
                )
                break

    if topology_mode == "repo_local" and ".github" in minimum_repo_set:
        errors.append(
            {
                "code": "minimum_repo_set_by_topology",
                "message": "repo_local may not require dedicated .github repo in minimum_repo_set_by_topology",
            }
        )
    if topology_mode == "dedicated_repo" and ".github" not in minimum_repo_set:
        errors.append(
            {
                "code": "minimum_repo_set_by_topology",
                "message": "dedicated_repo must require .github in minimum_repo_set_by_topology",
            }
        )
    if topology_mode == "repo_local" and "repo_local_only" not in placement_rules:
        errors.append(
            {
                "code": "governance_asset_placement_rules",
                "message": "repo_local must resolve to repo_local_only governance asset placement",
            }
        )
    if topology_mode == "hybrid" and "hybrid_split" not in placement_rules:
        errors.append(
            {
                "code": "governance_asset_placement_rules",
                "message": "hybrid must resolve to hybrid_split governance asset placement",
            }
        )
    if bundle.get("back_write_allowed") is not False:
        errors.append({"code": "back_write_allowed", "message": "back_write_allowed must be false"})
    if bundle.get("reinterpretation_allowed") is not False:
        errors.append({"code": "reinterpretation_allowed", "message": "reinterpretation_allowed must be false"})
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "topology_aware_offering_package_definition_resolution",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "package_level": package_level,
            "topology_mode": topology_mode,
            "source_definition_artifact_ref": source_definition_artifact_ref,
            "minimum_repo_set_by_topology": minimum_repo_set,
            "workflow_inclusion_level_by_topology": workflow_level,
            "governance_asset_placement_rules": placement_rules,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
