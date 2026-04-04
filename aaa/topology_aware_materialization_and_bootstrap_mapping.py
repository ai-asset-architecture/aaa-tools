import json
from pathlib import Path
from typing import Any


ALLOWED_TOPOLOGY_MODE = {"dedicated_repo", "repo_local", "hybrid"}
ALLOWED_MAPPING = {"org_repo_only", "repo_local_only", "hybrid_split"}
ALLOWED_SCOPE = {"org_repo", "repo_local", "split"}
ALLOWED_COMPLETENESS = {"complete", "partial"}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    topology_mode = str(bundle.get("topology_mode", "")).strip()
    mapping = bundle.get("materialization_mapping_by_topology", [])
    workflow_target_scope = str(bundle.get("workflow_target_scope", "")).strip()
    codeowners_target_scope = str(bundle.get("codeowners_target_scope", "")).strip()
    mapping_completeness = str(bundle.get("mapping_completeness", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "topology_aware_materialization_and_bootstrap_mapping":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be topology_aware_materialization_and_bootstrap_mapping",
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
    if not isinstance(mapping, list) or not mapping:
        errors.append(
            {
                "code": "materialization_mapping_by_topology",
                "message": "materialization_mapping_by_topology must be a non-empty array",
            }
        )
    else:
        for item in mapping:
            if str(item).strip() not in ALLOWED_MAPPING:
                errors.append(
                    {
                        "code": "materialization_mapping_by_topology",
                        "message": "materialization_mapping_by_topology includes an unsupported mapping",
                    }
                )
                break
    if workflow_target_scope not in ALLOWED_SCOPE:
        errors.append({"code": "workflow_target_scope", "message": "workflow_target_scope is not allowed"})
    if codeowners_target_scope not in ALLOWED_SCOPE:
        errors.append({"code": "codeowners_target_scope", "message": "codeowners_target_scope is not allowed"})
    if mapping_completeness not in ALLOWED_COMPLETENESS:
        errors.append({"code": "mapping_completeness", "message": "mapping_completeness is not allowed"})
    if bundle.get("materialization_scope_implies_governance_authority") is not False:
        errors.append(
            {
                "code": "materialization_scope_implies_governance_authority",
                "message": "materialization_scope_implies_governance_authority must be false",
            }
        )
    if bundle.get("package_active_asserted") is not False:
        errors.append({"code": "package_active_asserted", "message": "package_active_asserted must be false"})
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    if topology_mode == "dedicated_repo":
        if "org_repo_only" not in mapping:
            errors.append(
                {
                    "code": "materialization_mapping_by_topology",
                    "message": "dedicated_repo must include org_repo_only mapping",
                }
            )
        if workflow_target_scope == "repo_local":
            errors.append(
                {
                    "code": "workflow_target_scope",
                    "message": "dedicated_repo may not resolve workflows to repo_local only",
                }
            )
    if topology_mode == "repo_local":
        if "repo_local_only" not in mapping:
            errors.append(
                {
                    "code": "materialization_mapping_by_topology",
                    "message": "repo_local must include repo_local_only mapping",
                }
            )
        if workflow_target_scope == "org_repo":
            errors.append(
                {
                    "code": "workflow_target_scope",
                    "message": "repo_local may not resolve workflows to org_repo only",
                }
            )
        if codeowners_target_scope == "org_repo":
            errors.append(
                {
                    "code": "codeowners_target_scope",
                    "message": "repo_local may not resolve codeowners to org_repo only",
                }
            )
    if topology_mode == "hybrid":
        if "hybrid_split" not in mapping:
            errors.append(
                {
                    "code": "materialization_mapping_by_topology",
                    "message": "hybrid must include hybrid_split mapping",
                }
            )
        if workflow_target_scope != "split":
            errors.append(
                {
                    "code": "workflow_target_scope",
                    "message": "hybrid must resolve workflow_target_scope to split",
                }
            )
    if mapping_completeness == "partial" and topology_mode == "hybrid":
        errors.append(
            {
                "code": "mapping_completeness",
                "message": "hybrid mapping may not be marked partial",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "topology_aware_materialization_and_bootstrap_mapping",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "topology_mode": topology_mode,
            "materialization_mapping_by_topology": mapping,
            "workflow_target_scope": workflow_target_scope,
            "codeowners_target_scope": codeowners_target_scope,
            "mapping_completeness": mapping_completeness,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
