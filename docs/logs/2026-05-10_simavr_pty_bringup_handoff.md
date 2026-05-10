# Handoff - 2026-05-10 simavr PTY Bring-Up

## State

The ATMEGA2560 simulator path is now interactive and viable.

## What changed

- Added simulator metadata and contract notes:
  - `tools/sim/mega_vm_manifest.py`
  - `docs/architecture/mega_simulator_contract.md`
- Added simulator script folder:
  - `tools/sim/scripts`
- Added PTY-backed Mega harness:
  - `tools/sim/src/mega_vm_pty.c`
- Added PTY build/run scripts:
  - `tools/sim/scripts/build_mega_vm_pty.sh`
  - `tools/sim/scripts/run_mega_vm_pty.sh`
  - plus `.cmd` wrappers

## What was proved

- Plain `simavr` boots the Mega VM and prints the seed Forth banner.
- PTY-backed `simavr` plus `picocom` supports live interaction.
- Confirmed working commands:
  - `1 1 + .` -> `2 ok`
  - `: TST 41 EMIT ;` followed by `TST`

## Important detail

- The PTY harness currently uses:
  - `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`
- Reason:
  - the linked `libsimavr` build reported `ELF format is not supported by this build`
- The plain `simavr` CLI can still boot the ELF directly, but the custom PTY harness currently uses HEX.

## Current script flow

1. `tools/sim/scripts/build_mega_vm_pty.sh`
2. `tools/sim/scripts/run_mega_vm_pty.sh`
3. in another WSL shell:
   `tools/sim/scripts/run_mega_vm_picocom.sh`

## Next steps

1. Add an automated source-feed script for `.fs` files through `/tmp/simavr-uart0`
2. Capture console transcripts during source feed
3. Identify the exact runtime dictionary / CP / HERE state that must be extracted
4. Serialize the extracted post-compile image into a host artifact readable by the `.ino` ROM build path

## Notes for the next chat

- The important milestone is that simulated live seed compilation is now practical.
- The next work is not simulator evaluation anymore; it is feed/capture/extract automation.
