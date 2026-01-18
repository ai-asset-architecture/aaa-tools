---
name: dev-scaffold-mock
description: Generate MSW mock handlers from OpenAPI definitions to accelerate Mock-first development.
metadata:
  domain: development
  owner: Builder
  short-description: Mock 生成器
---

# Dev Scaffold Mock

## When to use
- Use when a new API endpoint is defined in `pbos-api-contracts`.
- Use when the user asks to "implement the mock" for a feature.

## Prerequisite
- The `openapi/v1.yaml` MUST be updated first (Contract-first).

## Execution Steps

1.  **Prepare Scaffolding**
    Run the script to create the target file and read the contract definition.
    Replace `<resource_name>` with the domain entity (e.g., `body-log`, `vitals`).
    
    ```bash
    node scripts/scaffold_handler.js <resource_name>
    ```

2.  **Generate Code (LLM Task)**
    - The script will output the relevant sections of `openapi/v1.yaml` (if found) and create a blank handler file at `pbos-mock-server/src/handlers/<resource_name>.ts`.
    - **Your Task**: Generate the `msw` (Mock Service Worker) code inside that file.
    - **Requirement**:
      - Import types from `pbos-shared-schemas` (if available).
      - Include both `http.get` (Success) and `http.post` (Success + Validation Error) scenarios.
      - Use `@faker-js/faker` to generate dynamic data.
