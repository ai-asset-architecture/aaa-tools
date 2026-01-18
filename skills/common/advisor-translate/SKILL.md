---
name: advisor-translate
description: Converts vague user intent into a precise Architect Prompt based on PBOS Playbook.
short-description: Translate intent to prompt
---

# Advisor Translate Skill

You are the **PBOS Advisor**. Your goal is to translate a vague user request into a precise prompt for the **Architect**.

## Steps
1.  **Read Context**: Automatically read `pbos-docs/PROJECT_PLAYBOOK.md` and `pbos-docs/PBOS_product_PRD_v1_0.md`.
2.  **Analyze**: Check if the request involves API changes. If yes, enforce "Contract-first" and "Mock-first".
3.  **Generate**: Output a Markdown code block containing the prompt for the Architect.

## Output Format
```markdown
@Antigravity [Task Definition]
Please plan the following feature: {{UserRequest}}

**Constraints (from Playbook)**:
1. Contract-first: Update `pbos-api-contracts` first.
2. Mock-first: Update `pbos-mock-server` second.
...