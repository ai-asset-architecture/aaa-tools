from pathlib import Path

from aaa import offering_package_selection_runtime_baseline as runtime


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "offering_package_selection",
    "line_class": "offering_package_runtime_enablement_line",
    "baseline_scope": "pre_topology_baseline",
    "post_topology_consumption_required": True,
    "topology_contract_ref": "v2.1.30",
    "package_level": "core",
    "selection_artifact_mode": "explicit_selection_artifact",
    "free_text_alias_allowed": False,
    "package_level_alias_forbidden": True,
    "definition_resolution_included": False,
    "prerequisite_judgment_included": False,
    "prose_fallback_allowed": False,
}


def test_validate_bundle_passes_for_canonical_selection():
    result = runtime.validate_bundle(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "offering_package_selection"
    assert result["derived_results"]["package_level"] == "core"


def test_validate_bundle_rejects_package_alias():
    bundle = dict(PASS_BUNDLE)
    bundle["package_level"] = "lite-bootstrap"

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "package_level" in result["error_codes"]


def test_validate_bundle_rejects_resolution_leakage():
    bundle = dict(PASS_BUNDLE)
    bundle["definition_resolution_included"] = True

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "definition_resolution_included" in result["error_codes"]


def _resolve_tpl_docs_example(example_name: str, folder: str) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = repo_root.parent
    candidates = [
        repo_root / "aaa-tpl-docs",
        workspace_root / "aaa-tpl-docs",
    ]
    for candidate_root in candidates:
        candidate = (
            candidate_root
            / "internal"
            / "development"
            / "contracts"
            / "ops"
            / "examples"
            / folder
            / example_name
        )
        if candidate.exists():
            return candidate
    return candidates[0] / "internal" / "development" / "contracts" / "ops" / "examples" / folder / example_name


def test_validate_bundle_file_uses_canonical_fixture():
    bundle_path = _resolve_tpl_docs_example(
        "2026-04-04-v2.1.23-offering-package-selection-runtime-baseline.pass.json",
        "pass",
    )

    result = runtime.validate_bundle_file(bundle_path)

    assert result["valid"] is True
    assert result["bundle_path"].endswith(
        "2026-04-04-v2.1.23-offering-package-selection-runtime-baseline.pass.json"
    )
