# Simulator Scripts

This folder holds small launch scripts for the current `simavr`-based Mega VM workflow.

## Current Scripts

- `bootstrap_simavr.sh`
  - Clone and build a repo-local `simavr` checkout under `avrsim/simavr` when the runtime does not already provide one.
- `run_mega_vm_simavr.sh`
  - Run the current Mega VM ELF under `simavr` from WSL/Linux.
- `run_mega_vm_simavr.cmd`
  - Windows `cmd` wrapper that launches the same `simavr` command through WSL.
- `run_mega_vm_picocom.sh`
  - Open `picocom` against the expected `simavr` UART PTY path.
- `run_mega_vm_picocom.cmd`
  - Windows `cmd` wrapper that launches the same `picocom` command through WSL.
- `build_mega_vm_pty.sh`
  - Build the PTY-backed Mega VM simulator harness against a repo-local simavr checkout, system install, or explicit `SIMAVR_*` paths.
- `build_mega_vm_pty.cmd`
  - Windows `cmd` wrapper that launches the PTY harness build through WSL.
- `run_mega_vm_pty.sh`
  - Run the PTY-backed Mega VM harness that creates `/tmp/simavr-uart0`.
- `run_mega_vm_pty.cmd`
  - Windows `cmd` wrapper that launches the PTY-backed Mega VM harness through WSL.
- `doctor_simavr.sh`
  - Diagnose simavr headers, libraries, CLI, harness link state, and supported setup options.
- `compile_forth_sources.sh`
  - Start the PTY-backed Mega VM harness and send repository Forth source files in one non-interactive command.
- `../send_forth_file.py`
  - Linux/WSL source feeder for sending one or more `.fs` files to `/tmp/simavr-uart0` without `picocom`.

## Notes

- Run `doctor_simavr.sh` first when the simulator cannot start; it prints discovered headers, libraries, and setup commands.
- Run `bootstrap_simavr.sh` first on a fresh Linux/WSL runtime if neither `simavr` nor a built `SIMAVR_ROOT` is available.  If network is unavailable, set `SIMAVR_ARCHIVE=/path/to/simavr.tar.gz` to unpack a supplied source tree instead of cloning.
- The direct `simavr -m atmega2560 -f 16000000 ...elf` path is currently useful for proving the Mega VM boots and prints the seed Forth banner.
- A `picocom` connection becomes useful after the PTY-backed harness creates `/tmp/simavr-uart0`.
- The PTY-backed harness currently defaults to `pdr_vm.ino.hex` so it does not depend on ELF-loader support in the linked `libsimavr`.
- `tools/sim/build/` is intentionally ignored; build `mega_vm_pty` locally with `build_mega_vm_pty.sh` rather than relying on a checked-in host binary.
- Typical sequence:
  - `./bootstrap_simavr.sh` if `simavr` is not already installed/built
  - `./build_mega_vm_pty.sh`
  - `./run_mega_vm_pty.sh`
  - in another WSL shell: `./run_mega_vm_picocom.sh` for manual use, or `python3 ../send_forth_file.py --source-list "../../forth/Forth Sources/build_order.txt" --log ../out/forth_compile_transcript.txt` for low-level scripted source feeding
  - for a single-command non-interactive compile attempt, run `./compile_forth_sources.sh` to compile `04-ansi.fs`, or `./compile_forth_sources.sh --source-list "../../forth/Forth Sources/build_order.txt"` to feed the repository build order
