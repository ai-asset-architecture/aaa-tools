# External Trial Evidence: AAA Public Preview

## Scope

This note records a minimal external-trial evidence pattern for AAA during public preview. It is intentionally small and factual: the goal is to show that the project is being prepared for use outside maintainer context, not to overstate adoption.

## Trial Objective

The trial objective is simple:

- verify that a first-time external user can understand what AAA is
- verify that `aaa-tools` is identifiable as the executable core
- verify that the quickstart path is understandable without private maintainer context

## Trial Path

The public-preview path being validated is:

1. Read the organization profile and `aaa-tools` README
2. Identify AAA's purpose and current capability surface
3. Install the CLI from the pinned release reference
4. Inspect the first commands: `aaa init validate-plan --help`, `aaa init --help`, `aaa run runbook --help`

## What This Trial Is Intended to Reveal

This trial is meant to surface first-contact problems such as:

- unclear project positioning
- confusion about which repository is the main entry point
- quickstart gaps
- unclear difference between public materials and internal evidence layers

## Current Public-Preview Evidence

The current public-preview preparation work includes:

- aligned public entry points in the org profile, workspace README, and `aaa-tools` README
- a public case study for agent-orchestrated engineering governance
- public OSS governance files in `aaa-tools`
- visible maintainer backlog items in GitHub issues
- active public-readiness cleanup PRs in adjacent AAA repositories

## Next Evidence to Add

The next stronger form of public evidence should include:

- the date of an external walkthrough
- the role or profile of the evaluator
- what confused them, if anything
- what documentation or workflow was changed in response

## Boundary

This is a public-preview evidence note, not a claim of broad production adoption. It exists to document the transition from maintainer-only context toward external OSS usability.
