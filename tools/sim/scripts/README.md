# Simulator Scripts

This folder now holds Windows batch wrappers for a copied `avrsim.exe`
artifact and the standard Windows terminal, Tera Term.

Expected artifact location:

- `avrsim/avrsim.exe`

Current wrappers:

- `run_mega_vm_simavr.cmd`
  - Launches the Windows `avrsim.exe` artifact against the default Mega
    firmware image.
- `run_mega_vm_teraterm.cmd`
  - Opens Tera Term against a serial port or named pipe endpoint.
- `run_mega_vm_pty.cmd`
  - Compatibility alias for `run_mega_vm_teraterm.cmd`.
- `build_mega_vm_pty.cmd`
  - Checks whether the `avrsim.exe` artifact exists and points you at the
    direct launcher and terminal wrapper.

Tera Term is selected through either:

- `AVRSIM_COM`
  - COM port number, for example `4` or `COM4`
- `AVRSIM_PIPE`
  - Named pipe name, for example `avrsim-uart0`

`run_mega_vm_teraterm.cmd` uses Tera Term's command line to open the selected
endpoint at `115200` baud.

The simulator launcher looks for the preferred firmware first:

1. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
2. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`
