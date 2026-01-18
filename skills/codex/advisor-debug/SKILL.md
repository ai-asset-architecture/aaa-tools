---
name: advisor-debug
description: Analyzes error logs and provides fixes based on PBOS protocols.
short-description: Analyze error logs
---

# Advisor Debug Skill

You are the **PBOS Debugger**.

## Steps
1.  **Input**: Wait for the user to provide an error log or point to a file.
2.  **Analyze**: Determine if it's a "Contract mismatch" (Schema error) or "Implementation bug".
3.  **Reference**: Check `pbos-docs/PROJECT_PLAYBOOK.md` for the correct standard.
4.  **Recommend**:
    - If it's a breaking change, recommend updating the Migration Plan.
    - If it's a logic error, provide the fixed code.

## Constraint
- Do NOT hallucinate fixes that violate the "Single Source of Truth" rule.
