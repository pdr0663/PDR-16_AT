# Handoff - 2026-05-10 Library Bring-Up

## State

Work shifted from "send `.fs` files over Tera Term" toward "find a simulator-backed way to compile libraries from seed Forth and emit artifacts to the host."

## What changed

- Patched `tools/forth/Assembler/eForth.asm.py` so `kTAP` ignores inline `LF`.
- Rebuilt the Forth ROM header and Arduino firmware.
- Uploaded the updated build to the Mega on `COM4`.
- Added a first-pass serial sender script:
  - `tools/forth/send_forth_file.ps1`

## What was learned

- The copied library sources in `tools/forth/Forth Sources` match the V5 originals.
- Those libraries are already precompiled into the ROM build path by:
  - `tools/forth/Assembler/precompile_phase1.py`
  - `tools/forth/Assembler/eForth.asm.py`
- Tera Term bulk text send still corrupts source input even after the `LF` fix, so line endings were only part of the problem.
- The current AT toolchain does not include the V5 packetized host terminal / host-backed file service.

## Simulator direction

Best current candidate appears to be `simavr` because it claims:

- `ATMega2560` support
- ELF loading
- UART support
- host-side project/peripheral emulation

Microchip Studio AVR Simulator and AVR8js/Wokwi are fallback candidates.

## Next steps

1. Audit which built artifact should be the simulator input, likely:
   - `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
2. Define exactly what compiled result must be captured:
   - runtime dictionary region and/or a simulated file sink
3. Prototype booting the current Mega firmware under a simulator
4. Prove console interaction
5. Compile a small library such as `04-ansi.fs` under seed Forth
6. Extract the resulting compiled artifact to the host

## Notes for the next chat

- Keep the handoff lightweight; avoid replaying the whole Tera Term debugging thread unless needed.
- The important pivot is from unreliable live serial loading toward a simulator-backed compile/capture workflow.

