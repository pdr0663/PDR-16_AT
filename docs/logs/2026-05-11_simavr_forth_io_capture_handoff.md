# 2026-05-11 simavr Forth source-feed and image-capture handoff

## Context

The simulator is now usable from the developer WSL environment: the Mega VM boots under `simavr`, UART interaction is good enough to reach the seed Forth system, and manual Forth console output is sensible.  The next objective is to make this workflow non-interactive:

1. start the Mega VM simulator;
2. feed one or more Forth source files into the simulated UART;
3. wait for compilation to finish and detect errors/faults;
4. extract a deterministic binary image of the post-compile Forth dictionary/RAM state.

This handoff records what is already present, what is missing, and the recommended next implementation path for a fresh chat.

## Current repository state relevant to this task

### Simulator launch and UART access

- `tools/sim/src/mega_vm_pty.c` is a small host-side `simavr` harness.  It loads a firmware image, creates an AVR instance, connects UART0 to `uart_pty`, and then runs the simulated CPU until it exits or crashes.
- `tools/sim/scripts/build_mega_vm_pty.sh` builds that harness against a local/system `simavr` checkout discovered through `tools/sim/scripts/simavr_env.sh`.
- `tools/sim/scripts/run_mega_vm_pty.sh` runs the harness and defaults to the Arduino CLI hex artifact, `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`.
- `tools/sim/scripts/run_mega_vm_picocom.sh` is the current manual console path.  It opens `/tmp/simavr-uart0` with `picocom` at `115200` baud.
- `tools/sim/scripts/run_mega_vm_simavr.sh` still supports direct `simavr -m atmega2560 -f 16000000 ...elf` execution, but that path is less useful for automated UART control than the PTY harness.

### Existing Forth source sender

- `tools/forth/send_forth_file.ps1` already implements the basic source-feeding behavior for a real serial port: open a port, send the source file line by line with carriage returns, wait for output to settle after each line, and fail if the response looks like a VM fault.
- That script is PowerShell/.NET `System.IO.Ports` based.  It is useful as a behavioral reference, but it is not yet a Linux/WSL PTY automation tool for `/tmp/simavr-uart0`.

### VM memory and capture contract

- `firmware/mega/pdr_vm/vm_config.h` defines the logical memory windows that matter for image capture:
  - ROM: `0x0000..0x7FFF`
  - low RAM/dictionary start: `0x8000..0x81FF`
  - high RAM: `0xF500..0xFFFF`
  - empty data stack: `0xF97F`
  - empty return stack: `0xFE7F`
- `firmware/mega/pdr_vm/vm_memory.h` stores the VM logical RAM in two C arrays inside the AVR firmware image: `g_vm_low_ram[VM_RAM_LOW_WORDS]` and `g_vm_high_ram[VM_RAM_HIGH_WORDS]`.
- `docs/architecture/mega_simulator_contract.md` and `tools/sim/mega_vm_manifest.py` already document the key capture goal: after compiling a Forth library under the Mega VM, capture the dictionary-bearing logical RAM regions and enough pointer state to reconstruct the image.

## Progress assessment

### Done

- The Mega VM firmware artifacts exist in the repo build directory:
  - `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
  - `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`
- The simulator support can discover/build/use `simavr` from WSL/Linux.
- The PTY harness creates a stable UART endpoint for automation: `/tmp/simavr-uart0`.
- The VM exposes console input/output through the Forth `?KEY` and `EMIT` primitives, backed by Arduino `Serial`/simavr UART0.
- There is a Windows serial feeder that demonstrates the desired line-oriented source-send policy.
- There is a manifest generator that emits memory-map and capture-contract metadata as JSON.

### Not done yet

- There is no Linux/WSL host feeder for sending `.fs` files to `/tmp/simavr-uart0` without `picocom`.
- There is no end-to-end script such as `compile_forth_image.sh` that starts the simulator, feeds a source list, captures logs, requests an image dump, and exits cleanly.
- There is no implemented binary extraction format yet.
- The current PTY harness is run-only.  It does not inspect simulated AVR SRAM or write any post-run artifact.
- The current default PTY harness input is the `.hex` file, which is good for loader compatibility but poor for host-side symbol-based extraction.  If host-side SRAM extraction is chosen, the harness will likely need an ELF path as the primary input so symbol addresses for `g_vm_low_ram` and `g_vm_high_ram` can be resolved.

## Important technical finding

The Forth-visible RAM to extract is not a single host-side buffer in the simulator harness.  It lives inside the simulated AVR firmware as AVR data memory:

- `g_vm_low_ram` contains logical `0x8000..0x81FF`.
- `g_vm_high_ram` contains logical `0xF500..0xFFFF`.

Therefore, image extraction has two plausible designs:

1. **Serial protocol extraction from inside the VM/Forth system**
   - Add a tiny debug/export word or monitor command that emits logical RAM words over UART in a deterministic text or binary format.
   - The Linux host feeder sends source files, then sends the export command, captures the UART output, and converts it to a binary image.
   - Advantage: works in simavr and on real hardware; avoids depending on simavr internals or ELF symbol lookup.
   - Disadvantage: consumes some target-side code/ROM space and requires a well-defined dump command/protocol.

2. **Host-side simavr memory extraction**
   - Run the PTY harness from the ELF, resolve the AVR data symbols `g_vm_low_ram` and `g_vm_high_ram`, read those bytes from simulated AVR SRAM after compilation, and write a host artifact directly.
   - Advantage: no UART dump traffic and no Forth-visible dump word needed.
   - Disadvantage: tied to simavr internals and ELF/debug-symbol availability; may not work from the current hex-only PTY path.

## Recommended next implementation path

Prefer **serial protocol extraction first** because it proves the same workflow can later run on physical hardware.  A practical staged plan:

### Stage 1: Linux PTY source feeder

Create a Python tool, probably `tools/sim/send_forth_file.py`, that mirrors `tools/forth/send_forth_file.ps1` but targets POSIX serial/PTY devices.

Suggested behavior:

- arguments:
  - `--port /tmp/simavr-uart0`
  - `--baud 115200` for real serial compatibility, even though PTYs ignore baud in practice
  - `--source <path>` repeatable, or `--source-list tools/forth/Forth Sources/build_order.txt`
  - `--inter-line-delay-ms`
  - `--prompt-timeout-ms`
  - `--log <path>`
- open the PTY with Python standard library modules (`os`, `termios`, `select`) so the repo does not need a new dependency just to talk to `/tmp/simavr-uart0`;
- normalize line endings to carriage return (`\r`), matching the PowerShell sender;
- capture all target output to a transcript;
- fail fast if output matches VM fault patterns such as `fault <n>` or `[PDR-16/XT VM fault ...]`;
- optionally wait for a known prompt/settled-output condition after each line.

### Stage 2: orchestration script

Create `tools/sim/scripts/compile_forth_image.sh` that:

1. ensures the PTY harness is built;
2. starts `run_mega_vm_pty.sh` in the background;
3. waits until `/tmp/simavr-uart0` exists;
4. invokes the Python source feeder for the selected source files;
5. sends the image-export command;
6. captures the export output and converts it to a binary artifact;
7. terminates the simulator process cleanly.

Initial outputs could live under `tools/sim/out/`, for example:

- `tools/sim/out/forth_compile_transcript.txt`
- `tools/sim/out/forth_ram_dump.txt`
- `tools/sim/out/forth_ram_image.bin`
- `tools/sim/out/forth_image_manifest.json`

Add `tools/sim/out/` to `.gitignore` unless a specific golden artifact is intentionally committed.

### Stage 3: target-side export word/protocol

Add a deliberately small export protocol.  Text first is easiest to debug:

```text
PDRDUMP1 LOW 8000 0200
8000 1234
8001 5678
...
PDRDUMP1 HIGH F500 0B00
F500 0000
...
PDRDUMP1 END
```

The host converter can parse this into a compact little-endian word image.  Once reliable, a binary framed format can replace or supplement the text format.

The export command should dump both logical RAM windows, not only the low dictionary area, because the high region contains stack/user areas and may hold state needed by the final image.

### Stage 4: dictionary boundary and metadata

Capture metadata after source compilation:

- final `CP @` / `HERE` value;
- current vocabulary/search state if needed for the saved image;
- source file list and hashes;
- firmware ELF/HEX path and hash;
- simulator command line;
- memory-map constants from `tools/sim/mega_vm_manifest.py`.

`tools/sim/mega_vm_manifest.py` already emits most static metadata; extend or reuse it rather than hard-coding addresses in the new host tools.

## Suggested first files to inspect in the next chat

- `tools/sim/src/mega_vm_pty.c` â€” current PTY-backed simulator harness.
- `tools/sim/scripts/run_mega_vm_pty.sh` â€” starts the PTY harness.
- `tools/sim/scripts/run_mega_vm_picocom.sh` â€” proves the PTY path used manually today.
- `tools/forth/send_forth_file.ps1` â€” behavior template for automated source feeding.
- `firmware/mega/pdr_vm/vm_config.h` â€” logical memory map constants.
- `firmware/mega/pdr_vm/vm_memory.h` â€” location of low/high RAM arrays.
- `docs/architecture/mega_simulator_contract.md` â€” existing capture contract.
- `tools/sim/mega_vm_manifest.py` â€” machine-readable manifest to feed future tooling.

## Suggested prompt for the next chat

```text
We need to continue the PDR-16/XT simavr automation work.  Please read docs/logs/2026-05-11_simavr_forth_io_capture_handoff.md first.  The goal is to add a Linux/WSL automated workflow that starts the PTY-backed simavr Mega VM, feeds Forth source files into /tmp/simavr-uart0, detects compile faults, and extracts a deterministic binary image of the post-compile Forth RAM/dictionary.  Prefer a serial export protocol first so the same mechanism can eventually work on physical hardware.
```

## Verification performed for this handoff

- Confirmed the repo currently has simulator scripts and a built PTY harness under `tools/sim`.
- Confirmed the PowerShell sender is the only existing source-file feeder.
- Confirmed the VM logical RAM windows and stack/user regions from `vm_config.h`.
- Confirmed logical RAM is stored in `g_vm_low_ram` and `g_vm_high_ram` inside the AVR firmware.
- Confirmed `mega_vm_manifest.py` already records a capture contract and static memory metadata.
