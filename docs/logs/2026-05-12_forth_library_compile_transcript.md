# 2026-05-12 Forth Library Compile Session Transcript

## Context

We split the simulator workflow so Explorer can launch explicit old/new IDE paths:

- `tools/sim/scripts/build_mega_vm_firmware_new.cmd`
- `tools/sim/scripts/build_mega_vm_firmware_old.cmd`
- `tools/sim/scripts/run_mega_vm_teraterm_new.cmd`
- `tools/sim/scripts/run_mega_vm_teraterm_old.cmd`
- `tools/sim/scripts/build_mega_vm_libraries_new.cmd`
- `tools/sim/scripts/build_mega_vm_libraries_old.cmd`

The goal for phase 2 is to replay `tools\forth\Forth Sources\build_order.txt` into the live Mega VM and watch for the resulting dictionary growth.

## What Happened

- Added a phase-2 wrapper that rebuilds firmware, starts the named-pipe bridge, and feeds Forth sources one line at a time.
- Added a PowerShell feeder that connects to the bridge pipe and logs the compile session.
- Initial runs exposed a few Windows workflow issues:
  - stale bridge processes could block the pipe connection
  - the feeder briefly used unsupported timeout settings on named pipes
  - the seed-image wrapper needed a no-pause mode for higher-level automation

## Important Observation

During a long compile run, the key thing to watch for is unexpected `ok` output while a colon definition is still being compiled.

That usually means:

- a lookup failed during compilation
- a word was missing
- or the interpreter dropped back into interpretation mode unexpectedly

If the build is healthy, progress should look like a steady stream of compile activity, not repeated stray `ok` responses in the middle of what should be a single definition.

## Current State

- The seed image build still works.
- The firmware build still works.
- The phase-2 compile feed reaches the live VM and starts producing output.
- The remaining work is to let the full replay finish cleanly and decide whether a deterministic image export step should be added next.
