# 2026-05-13 Forth Library Native Compile Transcript

This is a concise transcript of the chat turn that led to the native compile follow-up.

## Summary Of The Conversation

- The live-VM Forth library replay was working again after the earlier bridge and feeder fixes.
- The remaining problem was speed: some lines were taking roughly 10 seconds to compile.
- A native Windows compilation path was proposed as a possible solution.
- The discussion clarified that the current live path is intentionally conservative:
  - one line at a time
  - `XON/XOFF` flow control
  - blank lines skipped
  - full-line `\` comments skipped
- A native runner could be much faster, but it would not automatically be equivalent to the current AVR VM.
- The suggested next step is to inspect whether the existing Forth VM/compiler core can be separated from AVR-specific assumptions and reused with Windows-native I/O.

## Key Decisions

- Do not assume the AVR-emulated firmware can be compiled and run natively on Windows without adaptation.
- Treat a native Windows compiler/runner as a speed path that must be validated against the live VM.
- Keep the live-VM path as the reference implementation until equivalence is proven.

## Practical State At Handoff

- The live replay path is functional but slow.
- The bridge script has been adjusted to avoid waiting on blank lines and full-line comments.
- The next investigation target is architectural: how to build a native compile path without losing Forth semantics or source compatibility.
