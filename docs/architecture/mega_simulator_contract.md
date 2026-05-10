# Mega Simulator Contract

This note records the current simulator-facing contract for the ATMEGA2560 build so the simulation work can proceed from verified repo artifacts instead of assumptions.

## Confirmed Inputs

- Preferred simulator input artifact:
  - `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.elf`
- Fallback flash artifact:
  - `firmware/mega/pdr_vm/.build-cli/pdr_vm.ino.hex`
- Seed Forth ROM source artifacts:
  - `tools/forth/Assembler/eForth_lo.bin`
  - `tools/forth/Assembler/eForth_hi.bin`
  - `firmware/mega/pdr_vm/generated/pdr16_at_forth_image.h`

The generated Forth header currently exports `32768` logical ROM words, matching the VM's `0x0000..0x7FFF` logical ROM window.

## Current VM Contract

- Target MCU is `atmega2560` under the Arduino Mega build.
- Clock rate is `16 MHz`.
- Console traffic is bound to Arduino `Serial`, so simulator UART0 support is the first required peripheral.
- The VM cold-start vector is logical word address `0x0000`.
- The VM executes in fixed budgets of `256` VM steps per Arduino `loop()`.

## Memory Contract

- Logical ROM:
  - `0x0000..0x7FFF`
- Logical RAM, low region:
  - `0x8000..0x81FF`
- Logical RAM, high region:
  - `0xF500..0xFFFF`
- Initial dictionary growth starts at:
  - `0x8000`
- Empty stack pointers:
  - data stack `0xF97F`
  - return stack `0xFE7F`

The important detail for capture is that runtime dictionary growth is not one contiguous logical span. A simulator-backed export step will need to gather dictionary-bearing words across both RAM regions, not just dump a single block.

## What A Successful First Prototype Must Prove

1. The Mega ELF can boot in the simulator.
2. UART console interaction works well enough to drive seed Forth.
3. We can identify the final dictionary boundary after compiling a small library such as `04-ansi.fs`.
4. We can export the resulting logical RAM image back to the host in a deterministic format.

## Helper Script

Run:

```text
python tools/sim/mega_vm_manifest.py
```

That emits a JSON manifest containing the current artifact paths, logical memory map, serial settings, and the capture contract for future simulator harnesses.
