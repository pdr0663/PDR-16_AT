# Simulator Scripts

This folder holds small launch scripts for the current `simavr`-based Mega VM workflow.

## Current Scripts

- `run_mega_vm_simavr.sh`
  - Run the current Mega VM ELF under `simavr` from WSL/Linux.
- `run_mega_vm_simavr.cmd`
  - Windows `cmd` wrapper that launches the same `simavr` command through WSL.
- `run_mega_vm_picocom.sh`
  - Open `picocom` against the expected `simavr` UART PTY path.
- `run_mega_vm_picocom.cmd`
  - Windows `cmd` wrapper that launches the same `picocom` command through WSL.
- `build_mega_vm_pty.sh`
  - Build the PTY-backed Mega VM simulator harness against the local `simavr` tree.
- `build_mega_vm_pty.cmd`
  - Windows `cmd` wrapper that launches the PTY harness build through WSL.
- `run_mega_vm_pty.sh`
  - Run the PTY-backed Mega VM harness that creates `/tmp/simavr-uart0`.
- `run_mega_vm_pty.cmd`
  - Windows `cmd` wrapper that launches the PTY-backed Mega VM harness through WSL.

## Notes

- The direct `simavr -m atmega2560 -f 16000000 ...elf` path is currently useful for proving the Mega VM boots and prints the seed Forth banner.
- A `picocom` connection becomes useful after the PTY-backed harness creates `/tmp/simavr-uart0`.
- The PTY-backed harness currently defaults to `pdr_vm.ino.hex` so it does not depend on ELF-loader support in the linked `libsimavr`.
- Typical sequence:
  - `./build_mega_vm_pty.sh`
  - `./run_mega_vm_pty.sh`
  - in another WSL shell: `./run_mega_vm_picocom.sh`
