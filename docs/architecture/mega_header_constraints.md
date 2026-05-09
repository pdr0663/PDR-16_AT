# Arduino Mega header constraints

## Draft-schematic routing note

For the downward-facing header arrangement planned for this machine, avoid using the offset header region spanning:

- `SCL`
- `SDA`
- `D13` through `D8`

These pins are awkward mechanically because that header group is offset by half a hole pitch from the surrounding board-hole pattern.

## Reallocated draft pin usage

The draft remap moves the previously used `D8` through `D13` assignments onto `D14` through `D19`:

- `D8` -> `D14` for `CPLD_CS0`
- `D9` -> `D15` for `CPLD_CS1`
- `D10` -> `D16` for spare chip-select
- `D11` -> `D17` for spare chip-select
- `D12` -> `D18` for spare debug/control
- `D13` -> `D19` for `LED_DEBUG`

`D20` and `D21` were only reserved for optional I2C use, so in this draft they are simply marked as avoided rather than remapped.

## File

The revised draft pin allocation is captured in:

- `C:\Users\pdr0663\PDR-16_AT\MEGA Pinouts.reallocated.csv`

The original `MEGA Pinouts.csv` was left unchanged because it was locked by another process at edit time.
