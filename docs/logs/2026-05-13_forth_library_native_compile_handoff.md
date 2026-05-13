# 2026-05-13 Forth Library Native Compile Handoff

## Goal

Investigate a native Windows path for compiling the Forth libraries instead of replaying source line-by-line through the live Mega VM bridge.

## Why This Is Being Considered

- The current live-VM replay is functionally working, but some lines take about 10 seconds or more to complete.
- The slowdown is now understood to be real parser/compile latency, not just a simple host timeout bug.
- The current bridge path is conservative by design:
  - one source line at a time
  - blank lines skipped
  - full-line `\` comments skipped
  - wait for `XON` before the next line

## Current State

- `tools/sim/scripts/Other/compile_forth_libraries.ps1` now:
  - skips blank lines
  - skips full-line `\` comments
  - uses a longer activity-based wait for `XON`
  - logs a trace mode for debugging pipe reads
- The live-VM replay can now advance through `04-ansi.fs`, but it remains slow enough to be annoying for long comment-heavy sections.
- The library compile path is still tied to the live Mega VM and the named-pipe/Tera Term bridge.

## Native Compilation Idea

The suggestion is to build a native Windows system that can compile the library sources directly, without the AVR emulation layer.

This could mean one of two things:

1. A native build of the existing Forth VM/compiler core, with Windows-native I/O.
2. A separate native host-side compiler that consumes the same Forth sources but is not the AVR firmware itself.

## Important Constraint

Do not assume the AVR-emulated firmware can just be compiled as a regular Windows console app without adaptation.

The target currently depends on:

- AVR memory layout
- UART behavior
- target-specific words and side effects
- the exact current boot/compile environment

## Recommended Investigation Path

1. Identify which parts of the current compile loop are target-dependent and which are pure text processing.
2. Separate the Forth compiler/interpreter core from the AVR hardware assumptions.
3. If the core is sufficiently isolated, prototype a Windows-native runner for the compile/replay workload.
4. Compare output and dictionary state against the live-VM path on a small source subset first.
5. Keep the live-VM path as the reference until the native path is proven equivalent on the library set.

## Risks

- A native runner may compile faster but diverge subtly from the AVR VM.
- If the compile sources rely on exact target timing or memory behavior, native compilation may accept code that the target would not, or vice versa.
- A native path should be treated as a speed tool first, not as the authoritative build, until equivalence is demonstrated.

## Likely Next Step

Inspect the simulator and bridge structure to see whether the Forth VM already has a clean abstraction point for swapping the AVR backend out for a native Windows backend.
