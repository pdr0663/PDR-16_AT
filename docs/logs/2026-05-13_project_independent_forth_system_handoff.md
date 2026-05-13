# 2026-05-13 Project Independent Forth System Handoff

## Goal

Continue shaping the project-independent Forth system docs around a generic VM plus target-specific primitive packages.

## Current State

- The white paper now describes a generic target-agnostic VM.
- The new spec document defines:
  - the generic VM contract
  - the primitive contract
  - simulated and hardware primitive backends
  - build mode and interactive mode
  - library policy across targets
- The implementation language for the target backend is intentionally left open.

## Next Useful Steps

1. Add a short cross-reference from the `PDR-16_XT` broad-brush spec to the new project-independent Forth spec.
2. Decide the top-level repo name for the new portable project.
3. Draft a root README or mission statement for that new project.

## Notes

- Keep the generic VM target-neutral.
- Keep target-specific differences in primitive packages and target libraries.
- Keep the handoff lightweight.
