# Mega/CPLD local bus reservations

## Goal

Keep the **active** Mega-to-CPLD local interface at `8-bit`, but reserve a clean path for a later upgrade to `16-bit` local transfers without rethinking the whole pin map.

## Active now

The intended rev-A active local interface is:

- `MD[7:0]`
- `RA[3:0]`
- `RD#`
- `WR#`
- `START`
- `RESET`
- `CS0..CS3`
- `BUSY`
- `DONE`
- `IRQ_PENDING`
- `READ_DATA_READY`

This is enough for an `8-bit` register-oriented interface to the four CPLDs.

## Reserved for future 16-bit local communication

The following Mega pins are deliberately held aside for a possible future widening of the local bus:

- `D30..D37` reserved as `MD[15:8]`
- `D42..D49` reserved as `EXT[7:0]`
- `A8..A15` reserved if a later protocol wants a wider host-side address or sideband field

The point is not that all of these must be used. The point is to prevent rev-A wiring from casually consuming them elsewhere.

## CPLD-side reservation policy

On the CPLD side, reserve matching resources for:

- `MD[15:8]` visibility on any CPLD that might later participate in word transfers
- optional byte-lane / width control signals
- optional extra local readback or handshake signals

In practical terms:

- `data_path` should keep a plausible growth path for high-byte data handling
- `isa_ctrl_irq` should keep room for width-policy and lane-control support
- avoid using every spare I/O on those devices for unrelated convenience features

## Important architectural point

These reservations do **not** change the recommendation that rev-A communication remain `8-bit`.

They only preserve the option to widen the local Mega/CPLD bus later if experience shows it is worth the added routing and CPLD complexity.

## File

The reserved-pin draft is captured in:

- `C:\Users\pdr0663\PDR-16_AT\MEGA Pinouts.local_bus_reserved_16.csv`
