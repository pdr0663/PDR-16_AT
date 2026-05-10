# PDR-16/AT Forth Build Assets

This directory contains the initial Forth build machinery copied from the V5 reference system and trimmed for the `PDR-16_AT` MEGA-first draft.

## Scope

- The copied seed still binds console-facing words to simple primitive I/O:
  - `?KEY -> ?rx`
  - `EMIT -> tx!`
  - `EXPECT -> accept`
- The packetized host terminal and host-backed file service used by the V5 simulator are intentionally not part of this copied toolchain.
- Host file primitives remain in the primitive metadata for now because they are part of the V5 opcode surface, but the MEGA draft can leave them unimplemented until ISA-backed storage arrives.

## Layout

- [Assembler](C:/Users/pdr0663/PDR-16_AT/tools/forth/Assembler)
- [Forth Sources](C:/Users/pdr0663/PDR-16_AT/tools/forth/Forth%20Sources)
- [primitive_metadata.py](C:/Users/pdr0663/PDR-16_AT/tools/forth/Microcode%20Assembler/primitive_metadata.py)

## MEGA Draft Adjustments

- The copied assembler now uses half-sized data and return stacks to save SRAM in the initial MEGA-only system.
- Runtime dictionary growth still begins at logical word address `0x8000`.

## Rebuild And Export

Run:

```text
python tools\image_builder\export_forth_rom_header.py
```

That rebuilds the copied Forth image and emits:

- [pdr16_at_forth_image.h](C:/Users/pdr0663/PDR-16_AT/firmware/mega/pdr_vm/generated/pdr16_at_forth_image.h)

The generated header is intended for inclusion by the Arduino-side VM firmware.
