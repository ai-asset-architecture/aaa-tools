def post_init_repo_checks_hint() -> str:
    return "\n".join(
        [
            "Post-init DoD:",
            "  - Run: aaa init repo-checks --suite governance",
            "  - Purpose: post-init governance validation",
        ]
    )


def post_init_repo_checks_mcp_fields() -> dict:
    return {
        "post_init_required": ["aaa init repo-checks --suite governance"],
        "post_init_purpose": "post-init governance validation",
    }
