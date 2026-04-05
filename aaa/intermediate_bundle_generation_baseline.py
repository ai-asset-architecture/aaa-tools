"""
v2.1.42 Intermediate Bundle Generation Baseline
================================================
Generates command-emitted intermediate bundles for the canonical supported path.
Replaces client-authored prerequisite bundle generation with AAA-issued artifacts.

Runtime plane: intermediate_bundle_generation_baseline
Line class:    canonical_path_generation_line
Contract ref:  internal/development/contracts/ops/intermediate-bundle-generation-baseline.v0.1.schema.json
Step2 carrier: aaa-tools/.github/workflows/v2-1-42-intermediate-bundle-generation-baseline.yml
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


# ---------------------------------------------------------------------------
# Schema constants (mirror schema enums – no magic strings in business logic)
# ---------------------------------------------------------------------------

VALID_ARTIFACT_ORIGINS = frozenset({"command_emitted", "client_authored", "external_preexisting"})
VALID_GENERATION_STATUSES = frozenset({"automated_in_v2_1_42", "manual_pending", "topology_limited"})
VALID_TOPOLOGIES = frozenset({"dedicated_repo", "repo_local", "hybrid"})

RUNTIME_PLANE_MODE = "intermediate_bundle_generation_baseline"
LINE_CLASS = "canonical_path_generation_line"
SCHEMA_VERSION = "v0.1"


# ---------------------------------------------------------------------------
# Canonical intermediate artifact catalogue
# This catalogue is the single source of truth for what v2.1.42 generates
# vs what remains client-authored.  topology_constraints and
# profile_constraints are explicit – never implied.
# ---------------------------------------------------------------------------

ARTIFACT_CATALOGUE: list[dict[str, Any]] = [
    {
        "artifact_id": "prerequisite_bundle",
        "artifact_role": "prerequisite_gate_input",
        "artifact_origin": "command_emitted",
        "artifact_required_for_step": True,
        "artifact_not_auto_generated_in_v2_1_42": False,
        "generation_status": "automated_in_v2_1_42",
        "topology_constraints": ["dedicated_repo", "repo_local", "hybrid"],
        "profile_constraints": ["default", "local_sandbox"],
        "upstream_contract_ref": "v2.1.25",
    },
    {
        "artifact_id": "materialization_mapping_bundle",
        "artifact_role": "materialization_mapping_input",
        "artifact_origin": "command_emitted",
        "artifact_required_for_step": True,
        "artifact_not_auto_generated_in_v2_1_42": False,
        "generation_status": "automated_in_v2_1_42",
        "topology_constraints": ["dedicated_repo", "repo_local", "hybrid"],
        "profile_constraints": ["default", "local_sandbox"],
        "upstream_contract_ref": "v2.1.26",
    },
    {
        "artifact_id": "closeout_composition_bundle",
        "artifact_role": "closeout_input",
        "artifact_origin": "client_authored",
        "artifact_required_for_step": True,
        "artifact_not_auto_generated_in_v2_1_42": True,
        "generation_status": "manual_pending",
        "topology_constraints": ["hybrid"],
        "profile_constraints": ["default"],
        "upstream_contract_ref": "v2.1.29",
        "generation_gap_note": "hybrid closeout composition requires topology-split client knowledge not yet encoded",
    },
    {
        "artifact_id": "topology_closeout_bundle",
        "artifact_role": "topology_closeout_input",
        "artifact_origin": "client_authored",
        "artifact_required_for_step": True,
        "artifact_not_auto_generated_in_v2_1_42": True,
        "generation_status": "topology_limited",
        "topology_constraints": ["dedicated_repo", "repo_local"],
        "profile_constraints": ["default"],
        "upstream_contract_ref": "v2.1.36",
        "generation_gap_note": "topology closeout bundle generation depends on v2.1.44 init orchestration runtime",
    },
]


# ---------------------------------------------------------------------------
# Bundle builder
# ---------------------------------------------------------------------------

def build_generation_report(
    topology: str | None = None,
    profile: str | None = None,
) -> dict[str, Any]:
    """
    Build the generation report payload for the given topology/profile context.
    If topology is None, returns the full catalogue (all topologies).
    Validates topology against the legal enum before filtering.
    """
    if topology is not None and topology not in VALID_TOPOLOGIES:
        raise ValueError(
            f"topology must be one of {sorted(VALID_TOPOLOGIES)}, got: {topology!r}"
        )

    filtered_artifacts = [
        art for art in ARTIFACT_CATALOGUE
        if topology is None or topology in art["topology_constraints"]
    ]
    if profile is not None:
        filtered_artifacts = [
            art for art in filtered_artifacts
            if profile in art["profile_constraints"]
        ]

    automated = [a for a in filtered_artifacts if a["generation_status"] == "automated_in_v2_1_42"]
    pending = [a for a in filtered_artifacts if a["generation_status"] != "automated_in_v2_1_42"]

    return {
        "version": SCHEMA_VERSION,
        "runtime_plane_mode": RUNTIME_PLANE_MODE,
        "line_class": LINE_CLASS,
        "supported_path_fully_automated": False,
        "full_orchestration_provided": False,
        "full_execution_readiness_certified": False,
        "request_context": {
            "topology_filter": topology,
            "profile_filter": profile,
        },
        "generation_summary": {
            "total_artifacts": len(filtered_artifacts),
            "automated_in_v2_1_42": len(automated),
            "manual_pending": len(pending),
            "automation_ratio": (
                round(len(automated) / len(filtered_artifacts), 2)
                if filtered_artifacts else 0.0
            ),
        },
        "artifacts": filtered_artifacts,
        "gap_declaration": [
            {
                "artifact_id": a["artifact_id"],
                "generation_gap_note": a.get("generation_gap_note", "not yet automated"),
                "topology_constraints": a["topology_constraints"],
            }
            for a in pending
        ],
        "not_in_scope": [
            "full init orchestration pipeline (v2.1.44)",
            "readiness certification (v2.1.45)",
            "second public supported path",
            "client_authored gap auto-fill",
        ],
    }


def generate_prerequisite_bundle(topology: str, profile: str = "default") -> dict[str, Any]:
    """
    Generate the prerequisite_bundle artifact for the given topology/profile.
    This is the primary command_emitted artifact introduced in v2.1.42.
    """
    if topology not in VALID_TOPOLOGIES:
        raise ValueError(
            f"topology must be one of {sorted(VALID_TOPOLOGIES)}, got: {topology!r}"
        )
    return {
        "artifact_id": "prerequisite_bundle",
        "artifact_origin": "command_emitted",
        "generation_status": "automated_in_v2_1_42",
        "topology": topology,
        "profile": profile,
        "upstream_contract_ref": "v2.1.25",
        "payload": {
            "topology_expected": topology,
            "profile": profile,
            "gate_scope": "pre_adoption_prerequisite",
            "prerequisite_verdict_allowed_values": ["pass", "fail", "not_evaluable"],
            "prerequisite_verdict": "pass",
            "gate_verdict_not_activation": True,
            "gate_verdict_not_completion": True,
        },
    }


def generate_materialization_mapping_bundle(topology: str, profile: str = "default") -> dict[str, Any]:
    """
    Generate the materialization_mapping_bundle artifact for the given topology/profile.
    Second command_emitted artifact introduced in v2.1.42.
    """
    if topology not in VALID_TOPOLOGIES:
        raise ValueError(
            f"topology must be one of {sorted(VALID_TOPOLOGIES)}, got: {topology!r}"
        )

    placement_rule_map = {
        "dedicated_repo": "org_repo_only",
        "repo_local": "repo_local_only",
        "hybrid": "hybrid_split",
    }

    return {
        "artifact_id": "materialization_mapping_bundle",
        "artifact_origin": "command_emitted",
        "generation_status": "automated_in_v2_1_42",
        "topology": topology,
        "profile": profile,
        "upstream_contract_ref": "v2.1.26",
        "payload": {
            "topology": topology,
            "profile": profile,
            "governance_asset_placement_rule": placement_rule_map[topology],
            "workflow_target_scope": topology,
            "codeowners_scope": topology,
            "back_write_allowed": False,
            "reinterpretation_allowed": False,
        },
    }


# ---------------------------------------------------------------------------
# Schema validator (mirrors JSON Schema v0.1 required fields)
# ---------------------------------------------------------------------------

REQUIRED_KEYS = {
    "version",
    "runtime_plane_mode",
    "line_class",
    "supported_path_fully_automated",
    "full_orchestration_provided",
    "full_execution_readiness_certified",
    "artifacts",
}

REQUIRED_ARTIFACT_KEYS = {
    "artifact_id",
    "artifact_role",
    "artifact_origin",
    "artifact_required_for_step",
    "artifact_not_auto_generated_in_v2_1_42",
    "generation_status",
    "topology_constraints",
    "profile_constraints",
}


def validate_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Validate a bundle against the v2.1.42 schema contract.
    Returns a result dict with verdict and error list.
    """
    errors: list[str] = []

    # Top-level required keys
    missing_top = REQUIRED_KEYS - payload.keys()
    if missing_top:
        errors.append(f"missing required top-level keys: {sorted(missing_top)}")

    # Const constraints
    if payload.get("version") != SCHEMA_VERSION:
        errors.append(f"version must be {SCHEMA_VERSION!r}")
    if payload.get("runtime_plane_mode") != RUNTIME_PLANE_MODE:
        errors.append(f"runtime_plane_mode must be {RUNTIME_PLANE_MODE!r}")
    if payload.get("line_class") != LINE_CLASS:
        errors.append(f"line_class must be {LINE_CLASS!r}")
    if payload.get("supported_path_fully_automated") is not False:
        errors.append("supported_path_fully_automated must be false")
    if payload.get("full_orchestration_provided") is not False:
        errors.append("full_orchestration_provided must be false")
    if payload.get("full_execution_readiness_certified") is not False:
        errors.append("full_execution_readiness_certified must be false")

    # Artifacts array
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) < 1:
        errors.append("artifacts must be a non-empty array")
    else:
        for i, art in enumerate(artifacts):
            missing_art = REQUIRED_ARTIFACT_KEYS - art.keys()
            if missing_art:
                errors.append(f"artifact[{i}] missing keys: {sorted(missing_art)}")
            if art.get("artifact_origin") not in VALID_ARTIFACT_ORIGINS:
                errors.append(
                    f"artifact[{i}].artifact_origin must be one of {sorted(VALID_ARTIFACT_ORIGINS)}"
                )
            if art.get("generation_status") not in VALID_GENERATION_STATUSES:
                errors.append(
                    f"artifact[{i}].generation_status must be one of {sorted(VALID_GENERATION_STATUSES)}"
                )
            topo = art.get("topology_constraints", [])
            if not isinstance(topo, list) or len(topo) < 1:
                errors.append(f"artifact[{i}].topology_constraints must be non-empty list")
            else:
                invalid_topo = set(topo) - VALID_TOPOLOGIES
                if invalid_topo:
                    errors.append(f"artifact[{i}].topology_constraints has invalid values: {sorted(invalid_topo)}")
            prof = art.get("profile_constraints", [])
            if not isinstance(prof, list) or len(prof) < 1:
                errors.append(f"artifact[{i}].profile_constraints must be non-empty list")

    verdict = "pass" if not errors else "fail"
    payload_bytes = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode()
    inputs_digest = hashlib.sha256(payload_bytes).hexdigest()

    return {
        "verdict": verdict,
        "inputs_digest": inputs_digest,
        "error_count": len(errors),
        "errors": errors,
        "schema_ref": "intermediate-bundle-generation-baseline.v0.1.schema.json",
        "runtime_plane": RUNTIME_PLANE_MODE,
    }
