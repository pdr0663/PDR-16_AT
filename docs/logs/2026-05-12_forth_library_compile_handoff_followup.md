# 2026-05-12 Forth Library Compile Follow-up Handoff

## Goal

Keep the phase-2 Forth source replay working on the Mega VM without depending on `ok` as a sync point.

## Current Direction

- `CR` should still trigger `XOFF`.
- `XON` should be the explicit resume signal for the host.
- The bridge should forward control bytes to the host pipe.
- The feeder should wait on `XON` rather than guessing from quiet output alone.

## What Is Already In Place

- `tools/forth/Assembler/eForth.asm.py` has the `XOFF`/`XON` words and the current handshake edits.
- `tools/sim/src/mega_vm_teraterm.c` forwards raw control bytes to the pipe.
- `tools/sim/scripts/Other/compile_forth_libraries.ps1` has the terminal-safe output handling and line-wait logic.
- `tools/sim/scripts/build_mega_vm_firmware.cmd` accepts a custom build directory.
- `tools/sim/scripts/build_mega_vm_libraries.cmd` now uses a fresh build directory per run.

## Notes

- The banner text corruption is still a separate terminal-rendering symptom.
- The important remaining question is whether the line-level handshake is now deterministic enough for long source files.
- Keep this handoff lightweight and continue from the current pipe workflow.
