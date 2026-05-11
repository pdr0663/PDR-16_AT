# Simulator Scripts

This folder now separates the two simulator scenarios:

1. build the seeded Forth image from Python sources
2. run the resulting binary under `avrsim.exe` for system testing and
   development

Expected runtime artifact location:

- `avrsim/avrsim.exe`

Current entry points:

- `build_forth_image.cmd`
  - Rebuilds the seeded Forth image and generated header from the Python
    source tree.
- `run_mega_vm_simavr.cmd`
  - Launches `avrsim.exe` against the default Mega firmware image.
- `run_mega_vm_teraterm.cmd`
  - Opens Tera Term against the simulator serial endpoint.

Compatibility aliases:

- `build_mega_vm_pty.cmd`
  - Alias for `build_forth_image.cmd`.
- `run_mega_vm_pty.cmd`
  - Alias for `run_mega_vm_teraterm.cmd`.

Tera Term is selected through either:

- `AVRSIM_COM`
  - COM port number, for example `4` or `COM4`
- `AVRSIM_PIPE`
  - Named pipe name, for example `avrsim-uart0`

The direct launcher looks for the preferred firmware first:

1. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
2. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`
