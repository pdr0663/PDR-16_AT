# Simulator Scripts

This folder supports a Windows-only three-phase Forth/simulator workflow:

1. build the seeded Forth image from Python sources
2. run the Arduino Forth VM under the Windows UART harness, compile additional Forth
   source libraries, and save a new Forth image
3. run the Arduino Forth VM under the Windows UART harness again using that newly captured
   Forth image for further library work and general system use

Expected runtime artifact location:

- `tools/sim/bin/MegaVmTeraTerm/mega_vm_teraterm.exe`

Current entry points:

- `build_forth_image.cmd`
  - Rebuilds the seeded Forth image and generated header from the Python
    source tree for phase 1.
- `build_mega_vm_libraries.cmd`
  - Rebuilds the firmware and replays `tools\forth\Forth Sources\build_order.txt`
    into the live Mega VM over the named-pipe bridge. The script captures a
    transcript of the compile session and probes `WORDS` at the end.
- `build_mega_vm_firmware.cmd`
  - Rebuilds the current Forth image, then compiles the Arduino Mega firmware
    into `firmware/mega/pdr_vm/.build-cli` with `arduino-cli`.
- `build_and_run_mega_vm_simavr.cmd`
  - Rebuilds the current image, compiles the Mega firmware, then launches
    the Windows UART harness together with the Windows Tera Term bridge.
- `run_mega_vm_simavr.cmd`
  - Launches the Windows UART harness against the current Mega firmware image.
- `run_mega_vm_teraterm.cmd`
  - Builds the native named-pipe bridge, starts the UART harness, then opens Tera Term.
- `run_mega_vm_teraterm_new.cmd`
  - Explorer-friendly launcher for the Arduino IDE 2.x build output.
- `run_mega_vm_teraterm_old.cmd`
  - Explorer-friendly launcher for the Arduino IDE 1.8.x build output.
- `build_mega_vm_pipe_bridge.cmd`
  - Builds the native Windows UART bridge used by the Tera Term launcher from
    `tools/sim/src/mega_vm_teraterm.c`.
- `build_mega_vm_libraries_new.cmd`
  - Explorer-friendly phase-2 launcher for the Arduino IDE 2.x build output.
- `build_mega_vm_libraries_old.cmd`
  - Explorer-friendly phase-2 launcher for the Arduino IDE 1.8.x build output.

Current status by phase:

- Phase 1
  - Implemented. The Python builder emits the seeded ROM header consumed by the
    Mega VM firmware.
- Phase 2
  - Partially implemented. The Windows firmware build exists and the source
    feed into the live VM is now scripted, but deterministic binary export of
    the post-compile image is still the remaining major piece.
- Phase 3
  - Conceptually supported once phase 2 can emit a replacement image. The same
    firmware build and Windows UART harness launch path should then run against
    that captured image.

Compatibility aliases:

- `build_mega_vm_pty.cmd`
  - Alias for `build_forth_image.cmd`.
- `run_mega_vm_pty.cmd`
  - Alias for `run_mega_vm_teraterm.cmd`.

Note:

- The older PTY-backed notes in the repo are historical context from the
  Linux/WSL investigation path and are not part of the Windows-only workflow.

`build_mega_vm_firmware.cmd` accepts:

- `--skip-image`
  - Reuse the existing generated Forth image and only recompile the Arduino
    sketch.
- `--no-pause`
  - Suppress the Explorer pause so higher-level wrappers can chain additional
    steps.
- `--ide new`
  - Use the Arduino IDE 2.x / `arduino-cli` resolver under `tools/sim/ide/new/`.
- `--ide old`
  - Use the Arduino IDE 1.8.x / `arduino-builder` resolver under
    `tools/sim/ide/old/`.

`build_mega_vm_libraries.cmd` accepts:

- `--skip-image`
  - Reuse the current seeded image before replaying the library source list.
- `--ide new`
  - Use the Arduino IDE 2.x build output and the `arduino-cli` firmware path.
- `--ide old`
  - Use the Arduino IDE 1.8.x build output and the legacy firmware path.

`run_mega_vm_teraterm.cmd` accepts:

- `--ide new`
  - Use `firmware/mega/pdr_vm/.build-cli`.
- `--ide old`
  - Use `firmware/mega/pdr_vm/.build-legacy`.

Explorer-friendly explicit entry points:

- `build_mega_vm_firmware_new.cmd`
  - Hard-wired to the Arduino IDE 2.x path.
- `build_mega_vm_firmware_old.cmd`
  - Hard-wired to the Arduino IDE 1.8.x path.

`build_and_run_mega_vm_simavr.cmd` accepts:

- `--skip-image`
  - Skip the Forth image rebuild before recompiling the Arduino sketch.
- `--`
  - Separator before raw harness arguments, for example
    `build_and_run_mega_vm_simavr.cmd -- --gdb 1234`

Arduino CLI resolution order:

1. `ARDUINO_CLI_EXE`
2. `%ProgramFiles%\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe`
3. `where arduino-cli.exe`

The active resolver now lives under:

- `tools/sim/ide/new/resolve_arduino_cli.cmd`

The legacy Arduino IDE 1.8.x support subtree is reserved at:

- `tools/sim/ide/old/`

The legacy resolver returns the installed Arduino IDE root, which the build
wrapper uses to locate `arduino-builder.exe` and the bundled AVR toolchain.

Tera Term is selected through either:

- `AVRSIM_PIPE`
  - Named pipe name, for example `avrsim-uart0`

The Windows bridge now exposes UART0 to Tera Term over a named pipe and logs
the UART transcript to `tools\sim\logs\mega_vm_pipe_bridge.log` so future
debugging has an audit trail.

The bridge is a small native MinGW build. The wrapper uses the portable
toolchain in `C:\avrsim-portable\msys64\mingw64\bin\gcc.exe` and the
prebuilt simavr library in `C:\avrsim-portable\out`.

The direct launcher looks for the preferred firmware first:

1. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
2. `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`

That firmware currently embeds whatever Forth ROM header was last generated.
Today that is the seeded image from phase 1; after phase 2 is completed, this
same launch path is expected to run with a newly captured post-library image.
