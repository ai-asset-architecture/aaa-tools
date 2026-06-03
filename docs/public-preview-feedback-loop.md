# AAA Public Preview Feedback Loop

## Objective

Define a minimal external-trial loop for AAA during public preview so that first-time reviewer feedback becomes visible maintainer evidence rather than private context.

## Target External Trial Profiles

The current public-preview loop targets 3 to 5 evaluators from these profiles:

- OSS maintainers reviewing AI-assisted engineering tooling
- Staff or senior engineers evaluating governance and release discipline
- Developer tooling engineers who care about CLI usability and automation
- Security-minded reviewers validating bounded execution and approval surfaces
- AI-assisted product or platform teams deciding whether AAA is understandable outside maintainer context

## Minimal Onboarding Path

Each evaluator should be able to complete the following path:

1. Read the organization profile and the `aaa-tools` README
2. Identify AAA's purpose and why `aaa-tools` is the executable core
3. Install the pinned CLI or clone the repo for the bounded example path
4. Run the first safe commands in the quickstart
5. Report where the public path was unclear, stalled, or over-explained

## Feedback Capture

Maintainers should convert concrete external feedback into one of three public artifacts:

- a GitHub issue when the feedback identifies a narrow product or documentation gap
- a pull request when the feedback is already actionable and bounded
- an evidence note update when the feedback materially improves the public-preview story

## Current Public Preview Signals

The current public preview already has a visible loop:

- Issue `#2` captured first-time reviewer quickstart friction
- PR `#6` addresses that friction with runnable examples and a two-track quickstart
- `docs/case-studies/external-trial-public-preview.md` records the external README review feedback as public evidence

## Closure Standard

This loop should be considered healthy when:

- at least 3 external evaluator profiles have been targeted
- the onboarding path is explicit and runnable
- feedback themes become public issues or PRs
- resulting changes are traceable in README, tests, or evidence notes
