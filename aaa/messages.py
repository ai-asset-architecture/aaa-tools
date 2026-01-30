def post_init_repo_checks_hint() -> str:
    return "\n".join(
        [
            "Post-init DoD:",
            "  - Run: aaa init repo-checks --suite governance",
            "  - Purpose: post-init governance validation",
        ]
    )
