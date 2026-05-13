# 2026-05-13 Project Independent Forth System Transcript

This is a concise transcript of the discussion about splitting the Forth system into a portable project and target-specific primitive packages.

## Summary Of The Conversation

- The proposed portable Forth project should be separate from `PDR-16_XT`.
- The generic native VM is target-agnostic and should not know machine-specific details.
- Target-specific behavior belongs in primitive words and target libraries.
- Each target may provide two primitive backends:
  - a simulated backend for host-side development
  - a hardware backend for the actual system
- The same Forth library sources should be usable against both backends where compatible.
- The build system must be able to:
  - boot the core seed image
  - feed source into the VM
  - observe compile progress
  - receive the expanded binary
  - run the VM interactively after the build
- The target backend implementation language is intentionally not fixed.
- A target backend may be written in C, another C dialect, another systems language, assembly, or something else that satisfies the contract.

## Decisions Captured

- Keep the generic VM ignorant of target specifics.
- Treat primitives as the main target boundary.
- Allow target projects to define their own simulated and hardware primitive implementations.
- Keep the same library source code across simulation and hardware where the primitive contract permits.

## Result

- The architecture docs were updated to reflect the new project split.
- A new spec document was added for the project-independent Forth system.
