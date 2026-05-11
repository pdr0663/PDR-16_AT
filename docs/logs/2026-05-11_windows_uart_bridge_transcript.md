# 2026-05-11 Windows UART bridge transcript

## Context

This chat moved the simulator workflow from a boot-only Windows `avrsim`
launcher to a working Windows-only interactive UART path with Tera Term.

The key requirement was to keep everything in Windows, avoid WSL, and make the
Forth console interactive so future library development can be debugged from
the host side.

## What changed during the chat

### Simulator bridge

- The earlier host-process stdio relay was identified as the wrong layer for
  UART interaction.
- A native Windows UART harness was added in
  `tools/sim/src/mega_vm_teraterm.c`.
- The harness creates a named pipe for Tera Term and connects that pipe to
  AVR UART0 through simavr IRQs.
- UART traffic is logged to `tools/sim/logs/mega_vm_pipe_bridge.log` so future
  debugging has a transcript trail.

### Build and launch flow

- The bridge build script was updated to use the portable MinGW bundle in
  `C:\avrsim-portable`.
- The launcher in `tools/sim/scripts/run_mega_vm_teraterm.cmd` now starts the
  native harness and then opens Tera Term on `\\.\pipe\PDR16_AT_UART0`.
- The launcher path no longer depends on WSL or on the older C# bridge.

### Verification

- A synthetic named-pipe client confirmed the bridge connects successfully.
- The Forth banner is now visible through the UART side of the bridge.
- Tera Term is now usable for interactive work against the simulator.

## Current state

The interactive Windows-only simulator loop is now working.

The next practical task is to use that loop to check library inclusion and
continue the phase-2 compile/capture work.

## Notes for the next chat

- Keep the workflow Windows-only.
- Keep Tera Term as the interactive client.
- Use the native UART harness in `tools/sim/src/mega_vm_teraterm.c`.
- The bridge log in `tools/sim/logs/mega_vm_pipe_bridge.log` is the first
  place to inspect if UART behavior regresses.
