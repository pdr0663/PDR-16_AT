# Handoff - 2026-05-10 MEGA VM

## Status

The first Arduino Mega draft VM is working interactively.

Observed good state:

- boots to Forth sign-on
- reaches `ok`
- accepts console input
- `1 2 + .` returns `3 ok`
- smoke tests for stack ops, colon defs, variables, `HERE`, and `WORDS` all passed

## Important files

- `firmware/mega/pdr_vm/pdr_vm.ino`
- `firmware/mega/pdr_vm/vm_config.h`
- `firmware/mega/pdr_vm/vm_state.h`
- `firmware/mega/pdr_vm/vm_memory.h`
- `firmware/mega/pdr_vm/vm_serial.h`
- `firmware/mega/pdr_vm/vm_primitives.h`
- `firmware/mega/pdr_vm/vm_dispatch.h`
- `tools/image_builder/export_forth_rom_header.py`

## Key fixes already made

1. ROM header export changed from one huge AVR `PROGMEM` array to chunked arrays.
2. ROM reads changed to generated chunk-aware far reads.
3. `C!` was fixed so this word-addressed draft does not truncate seeded 16-bit values during `COLD`/`CMOVE`.
4. High logical RAM window was widened downward to cover the working input/scratch region.
5. Most temporary debug probes were removed after successful smoke tests.

## Current resource picture

Last clean compile reported roughly:

- flash: `71644` bytes
- globals: `7077` bytes
- free SRAM headroom: about `1115` bytes

Memory is still tight. Be careful with further RAM growth.

## Next sensible steps

1. Do a more systematic regression smoke test from the Forth prompt.
2. Trim SRAM usage if possible.
3. Revisit the top RAM window sizing with better knowledge of the actual required scratch region.
4. Decide whether to preserve current word-addressed `C@`/`C!` semantics for the draft as-is, or split byte/cell behavior more explicitly later.

## CLI notes

`arduino-cli` worked reliably for compile/upload once the port was free.

Useful commands used in this session:

```powershell
& 'C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe' compile --fqbn arduino:avr:mega --build-path 'C:\Users\pdr0663\PDR-16_XT\firmware\mega\pdr_vm\.build-cli' 'C:\Users\pdr0663\PDR-16_XT\firmware\mega\pdr_vm'
```

```powershell
& 'C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe' upload -p COM4 --fqbn arduino:avr:mega --input-dir 'C:\Users\pdr0663\PDR-16_XT\firmware\mega\pdr_vm\.build-cli' 'C:\Users\pdr0663\PDR-16_XT\firmware\mega\pdr_vm'
```

If uploads fail, the usual cause was `COM4` being open in the IDE serial monitor or Tera Term.

