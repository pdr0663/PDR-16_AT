# 2026-05-12 Forth Library Compile Handoff

## Goal

Finish the phase-2 flow that compiles the Forth library sources inside the Mega VM using `build_order.txt`.

## Current Working Pieces

- Explicit old/new Explorer launchers exist for firmware build and Tera Term launch.
- `tools/sim/scripts/build_mega_vm_libraries_old.cmd` and `..._new.cmd` start the phase-2 flow.
- The PowerShell feeder sends one source line at a time to the bridge pipe.

## Key Debug Signal

Watch the serial/pipe output while a colon definition is in progress.

If the interpreter prints `ok` in the middle of a definition that should still be compiling, that is a strong sign of:

- a missing word
- a failed lookup
- or a compile-mode fallback

That is the first thing to check before assuming the run is just slow.

## Notes

- Stale `mega_vm_teraterm.exe` bridge processes can block the next run; kill them before restarting.
- The phase-2 automation is still transcript-oriented. A deterministic post-compile image export is not wired yet.
- Keep the handoff lightweight and continue from the current batch/pipe workflow rather than redoing the seed-image work.
