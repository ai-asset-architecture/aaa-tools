import json
from pathlib import Path
from typing import Any


ALLOWED_PACKAGE_LEVEL = {"lite", "core", "full"}
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
ALLOWED_WORKFLOW_LEVEL = {"reduced", "core", "full"}
ALLOWED_CLIENT_PREREQUISITES = {
    "basic_ci",
    "ci_discipline",
    "contract_first",
    "mock_first",
    "review_evidence_discipline",
    "asset_feedback_loop",
    "ai_governance",
}
SOURCE_DEFINITION_ARTIFACT_REF = "aaa-docs/bootstrap/offering_definition_skeleton.md"


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    package_level = str(bundle.get("package_level", "")).strip()
    source_definition_artifact_ref = str(bundle.get("source_definition_artifact_ref", "")).strip()
    minimum_repo_set = bundle.get("minimum_repo_set", [])
    workflow_inclusion_level = str(bundle.get("workflow_inclusion_level", "")).strip()
    client_prerequisites = bundle.get("client_prerequisites", [])

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "offering_package_definition_resolution":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be offering_package_definition_resolution",
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
    if bundle.get("topology_resolution_precedence_ref") != "v2.1.32":
        errors.append(
            {
                "code": "topology_resolution_precedence_ref",
                "message": "topology_resolution_precedence_ref must be v2.1.32",
            }
        )
    if package_level not in ALLOWED_PACKAGE_LEVEL:
        errors.append({"code": "package_level", "message": "package_level is not allowed"})
    if bundle.get("source_definition_artifact") != SOURCE_DEFINITION_ARTIFACT_REF:
        errors.append(
            {
                "code": "source_definition_artifact",
                "message": "source_definition_artifact must point to the offering mother draft",
            }
        )
    if source_definition_artifact_ref != SOURCE_DEFINITION_ARTIFACT_REF:
        errors.append(
            {
                "code": "source_definition_artifact_ref",
                "message": "source_definition_artifact_ref must point to the offering mother draft",
            }
        )
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
    if workflow_inclusion_level not in ALLOWED_WORKFLOW_LEVEL:
        errors.append(
            {
                "code": "workflow_inclusion_level",
                "message": "workflow_inclusion_level is not allowed",
            }
        )
    if not isinstance(client_prerequisites, list) or not client_prerequisites:
        errors.append(
            {
                "code": "client_prerequisites",
                "message": "client_prerequisites must be a non-empty array",
            }
        )
    else:
        unsupported_prerequisites = [
            item for item in client_prerequisites if str(item).strip() not in ALLOWED_CLIENT_PREREQUISITES
        ]
        if unsupported_prerequisites:
            errors.append(
                {
                    "code": "client_prerequisites",
                    "message": "client_prerequisites includes unsupported prerequisite identifiers",
                }
            )
    if bundle.get("back_write_allowed") is not False:
        errors.append({"code": "back_write_allowed", "message": "back_write_allowed must be false"})
    if bundle.get("reinterpretation_allowed") is not False:
        errors.append({"code": "reinterpretation_allowed", "message": "reinterpretation_allowed must be false"})
    if bundle.get("dedicated_github_universal_invariant") is not False:
        errors.append(
            {
                "code": "dedicated_github_universal_invariant",
                "message": "dedicated_github_universal_invariant must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "offering_package_definition_resolution",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "package_level": package_level,
            "source_definition_artifact_ref": source_definition_artifact_ref,
            "topology_resolution_precedence_ref": bundle.get("topology_resolution_precedence_ref"),
            "minimum_repo_set": minimum_repo_set,
            "workflow_inclusion_level": workflow_inclusion_level,
            "client_prerequisites": client_prerequisites,
            "post_topology_consumption_required": bundle.get("post_topology_consumption_required"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
