# avrsim Source Build Architecture

This note defines the Windows-only three-phase simulator workflow for
`PDR-16/AT`.

1. Build the Forth system image from the Python seed plus Forth library source
   tree.
2. Run the Arduino Forth VM under the Windows UART harness, compile Forth source libraries
   inside the target VM, and capture a new Forth image.
3. Run the Arduino Forth VM under the Windows UART harness again using that captured image
   for further library development and general system use.

The important split is that seed image generation, simulator-assisted image
growth, and later simulator/runtime use are distinct stages. Phase 1 is still
Python-led; phases 2 and 3 depend on the Arduino VM running under the Windows
UART harness inside Windows.

## Phase 1: Build The Seed Forth Image

The image build starts from the Python seed build in:

- `tools/image_builder/export_forth_rom_header.py`

The Windows wrapper for that step is:

- `tools/sim/scripts/build_forth_image.cmd`

That script rebuilds the copied Forth image and emits the generated ROM header:

- `firmware/mega/pdr_vm/generated/pdr16_at_forth_image.h`

It also refreshes the split ROM binaries under:

- `tools/forth/Assembler/eForth_lo.bin`
- `tools/forth/Assembler/eForth_hi.bin`

This is the initial seeded image used to boot the Mega VM.

## Phase 2: Compile Libraries Under The Windows UART Harness And Capture A New Image

The simulator runtime is the Windows UART harness:

- `tools/sim/bin/MegaVmTeraTerm/mega_vm_teraterm.exe`

That binary is built on this machine against the portable MinGW simavr bundle.
It is used to run the Arduino Mega VM while Forth source is compiled inside the
target system.

The direct runtime launcher is:

- `tools/sim/scripts/run_mega_vm_simavr.cmd`

The firmware build step is:

- `tools/sim/scripts/build_mega_vm_firmware.cmd`

Together those steps provide the Windows-side launch path for phase 2. The
remaining missing automation is the target-side library compile/capture loop
and the Windows-native UART bridge:

- start the VM under the Windows UART harness
- feed Forth library sources to the VM
- detect compile failures
- extract and save the resulting post-compile Forth image
- expose UART0 to a Windows terminal over a pipe or COM endpoint

The current firmware launcher loads the preferred firmware artifact from:

1. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
2. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`

That firmware currently embeds the last generated Forth ROM header. Right now
that is the phase 1 seeded image.

## Phase 3: Run The Captured Post-Library Image

Once phase 2 can emit a new Forth image, the normal Mega firmware build plus
Windows UART harness launch path becomes the steady-state development/runtime
loop.

In other words:

1. replace the generated ROM/header input with the captured phase 2 image
2. rebuild the Mega VM firmware
3. launch under the Windows UART harness for further work

## Artifact Drop Location

Use `tools/sim/bin/` as the simulator artifact drop location.

Typical contents are:

- `MegaVmTeraTerm/mega_vm_teraterm.exe`

## Windows Terminal

Use Tera Term for interactive serial access on Windows.

The Windows wrapper is:

- `tools/sim/scripts/run_mega_vm_teraterm.cmd`

It now builds and starts a Windows named-pipe bridge before opening Tera Term.
The bridge connects to either:

- `AVRSIM_PIPE`
  - a named pipe such as `avrsim-uart0`

The older PTY notes in `docs/logs` came from the Linux/WSL investigation path.
They are useful background, but the supported direction here is a Windows-only
bridge and terminal workflow.

The bridge mirrors UART traffic to `tools/sim/logs/mega_vm_pipe_bridge.log`
so we can review terminal and simulator behavior after the fact when
debugging future firmware or library changes.

The bridge implementation lives in
`tools/sim/src/mega_vm_teraterm.c` and is built by
`tools/sim/scripts/build_mega_vm_pipe_bridge.cmd` with the portable MinGW
toolchain in `C:\avrsim-portable`.

## Responsibilities

The build machine is responsible for:

- building `simavr`
- gathering the runtime DLLs
- building the Windows UART harness

This machine is responsible for:

- running `export_forth_rom_header.py` when the Forth image must be rebuilt
- compiling `firmware/mega/pdr_vm` with `arduino-cli`
- launching the Windows UART harness for testing
- automating target-side Forth library compile/capture for phase 2
- using Tera Term for interactive serial work
- processing post-compile binaries and manifests
- implementing the Windows UART bridge if the current simulator binary does not
  already expose one

## Windows Build Entry Points

Now that the Windows UART harness exists in `tools/sim/bin/`, the normal local
workflow is:

1. phase 1 seed build via `tools/sim/scripts/build_forth_image.cmd`
2. Mega firmware build via `tools/sim/scripts/build_mega_vm_firmware.cmd`
3. simulator launch via `tools/sim/scripts/run_mega_vm_simavr.cmd`

Or in one step:

- `tools/sim/scripts/build_and_run_mega_vm_simavr.cmd`

`build_mega_vm_firmware.cmd`:

- regenerates the seeded Forth ROM header unless `--skip-image` is passed
- locates `arduino-cli.exe`
- compiles the Mega sketch into `firmware/mega/pdr_vm/.build-cli`

## Tooling That Still Matters

The current repo still keeps helper metadata because it remains useful across
all three phases:

- `tools/sim/mega_vm_manifest.py` records the memory map and capture contract.
- `tools/sim/send_forth_file.py` is only relevant if we later revive an
  automated serial feeder.

At the moment, phase 1 is implemented cleanly, the Windows firmware build and
simulator launch for phase 2 are implemented, and the missing core work is the
automated compile/capture loop that turns simulator-side library compilation
into a reusable post-library image for phase 3.
