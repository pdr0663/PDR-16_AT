# avrsim Source Build Architecture

This note defines the two simulator workflows for `PDR-16/AT`.

1. Build the Forth system image from the Python seed plus Forth library source
   files.
2. Run the resulting binary under `avrsim.exe` for system testing and
   development.

The important split is that image generation and simulator runtime are separate
steps. That matches the old Python-led Forth build model: Python is the source
of truth for the image, and the simulator consumes the generated artifact.

## Workflow 1: Build The Forth Image

The image build starts from the Python seed build in:

- `tools/image_builder/export_forth_rom_header.py`

That script rebuilds the copied Forth image and emits the generated ROM header:

- `firmware/mega/pdr_vm/generated/pdr16_at_forth_image.h`

It also refreshes the split ROM binaries under:

- `tools/forth/Assembler/eForth_lo.bin`
- `tools/forth/Assembler/eForth_hi.bin`

This is the scenario for "build the Forth system from source".

## Workflow 2: Run The Resulting Binary

The simulator runtime is a separate Windows artifact:

- `avrsim/avrsim.exe`

That binary is built on a Windows machine and copied into this repo. It is used
to run the generated Forth image for testing and development.

The direct runtime launcher is:

- `tools/sim/scripts/run_mega_vm_simavr.cmd`

That launcher loads the preferred firmware artifact from:

1. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
2. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`

## Artifact Drop Location

Use the `avrsim/` folder in this repo as the simulator artifact drop location.

That folder holds copied Windows build outputs and is ignored for binary files.

Typical contents are:

- `avrsim.exe`
- `libsimavr.a`
- `libsimavrparts.a`
- any DLLs needed by the executable or helper tools

## Windows Terminal

Use Tera Term for interactive serial access on Windows.

The Windows wrapper is:

- `tools/sim/scripts/run_mega_vm_teraterm.cmd`

It can connect to either:

- `AVRSIM_COM`
  - a COM port number such as `4` or `COM4`
- `AVRSIM_PIPE`
  - a named pipe such as `avrsim-uart0`

## Responsibilities

The build machine is responsible for:

- building `simavr`
- gathering the runtime DLLs
- copying `avrsim.exe` into `avrsim/`

This machine is responsible for:

- running `export_forth_rom_header.py` when the Forth image must be rebuilt
- launching `avrsim.exe` for testing
- using Tera Term for interactive serial work
- processing post-compile binaries and manifests

## Tooling That Still Matters

The current repo still keeps helper metadata because it remains useful for the
two workflows:

- `tools/sim/mega_vm_manifest.py` records the memory map and capture contract.
- `tools/sim/send_forth_file.py` is only relevant if we later revive an
  automated serial feeder.

For now, the source-of-truth build path is the Python image builder, and the
runtime path is the copied Windows `avrsim.exe` plus Tera Term.
