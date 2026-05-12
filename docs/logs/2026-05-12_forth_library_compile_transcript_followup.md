# 2026-05-12 Forth Library Compile Follow-up Transcript

## Context

We were continuing the phase-2 Mega VM Forth library replay from `tools\forth\Forth Sources\build_order.txt`.
The working goal was to avoid relying on the visible `ok` prompt and instead use explicit flow control around line boundaries.

## What Happened

- Added `XOFF` on `CR` so the host pauses once the current input line is complete.
- Moved `XON` between the interpreter's line-processing phases so the host can resume without watching the prompt text.
- Reworked the Windows pipe bridge to forward raw `XON`/`XOFF` control bytes instead of inferring state from terminal output.
- Tightened the PowerShell feeder so it handles empty chunks and terminal control characters without crashing.
- Added a unique per-run firmware build directory so stale `.build-cli` locks do not block subsequent runs.

## Debugging Notes

- The visible banner text was badly garbled, but the raw bridge log showed the target was still emitting output.
- The main remaining failure mode was synchronization, not a syntax error in the Forth source.
- Several host-side helpers had to be relaxed so empty reads and control-byte-only chunks would not abort the run.
- The first real sign of trouble in the source feed was that a normal compile line could complete, but the host still timed out waiting for the wrong completion condition.

## Current State

- The bridge and feeder changes are in place.
- The handshake now centers on `XOFF`/`XON`, not the `ok` prompt.
- The next run should verify whether line-ready signaling is now stable enough for the full `04-ansi.fs` replay.
