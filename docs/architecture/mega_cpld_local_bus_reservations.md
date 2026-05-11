# Mega/CPLD local bus interface

## Goal

Define the active Mega-to-CPLD local interface for the fixed two-PLD, 8-bit PDR-16/XT design.

This note no longer reserves pins for a later 16-bit local-bus expansion. The intention is to document the actual interface we mean to build.

## Active interface

The intended local interface is:

- `MD[7:0]`
- `RA[3:0]`
- `RD#`
- `WR#`
- `START`
- `RESET`
- `CS0..CS1`
- `BUSY`
- `DONE`
- `IRQ_PENDING`
- optional `READ_DATA_READY`

This is enough for an 8-bit register-oriented interface to two CPLDs.

## CPLD-side policy

The CPLDs should spend their pins on the fixed XT-class bus path rather than on hypothetical width growth:

- latch ISA address and control fields
- drive `SA[19:0]`
- drive or sample `SD[7:0]`
- sequence `IOR#`, `IOW#`, `MEMR#`, and `MEMW#`
- return read data and status to the Mega
- collect a practical subset of ISA IRQ inputs

## Architectural point

The internal PDR machine remains 16-bit and word-oriented.

The local Mega/CPLD link and the external ISA bus are both intentionally 8-bit oriented. Byte-wide interaction is part of the design, not a temporary concession.

## File

The reserved-pin draft is captured in:

- `C:\Users\pdr0663\PDR-16_XT\MEGA Pinouts.local_bus_reserved_16.csv`

That filename is historical. Its contents should be interpreted as a pin-allocation worksheet, not as evidence of a planned 16-bit bus upgrade.
