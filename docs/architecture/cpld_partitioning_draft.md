# CPLD partitioning draft

## Short answer

No, the Mega does **not** need to transfer full parallel address and data buses directly into the CPLDs.

That would consume pins very quickly and is not the best fit for three `ATF1504AS` devices.

A better structure is:

- the Mega talks to the CPLD cluster over a **shared narrow local register interface**
- the CPLDs latch address, data, and cycle-control bytes internally
- the CPLDs then generate the ISA bus cycle from those latched registers

In other words, the Mega should act more like it is programming a bus engine than bit-banging a raw external bus.

## Important package note

This draft assumes you are using an `ATF1504AS` package with about `64 user I/O pins` such as the `84-lead PLCC` or `100-lead TQFP`.

Microchip's datasheet shows:

- `44-lead TQFP`: `32 user I/O pins`
- `44-lead PLCC`: `32 user I/O pins`
- `84-lead PLCC`: `64 user I/O pins`
- `100-lead TQFP`: `64 user I/O pins`

Source:

- [Microchip ATF1504AS(L) datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/ATF1504AS%28L%29-5V-64-Macrocell-CPLD-Data-Sheet-20006580A.pdf)

If you are using the `44-pin` parts, this whole allocation gets much tighter and may need external latches or transceivers.

## Recommended Mega-to-CPLD interface

Use a shared local interface like this:

- `MD[7:0]` shared local data bus from Mega to all three CPLDs
- `RA[3:0]` local register address bus
- `RD#`
- `WR#`
- `START`
- `RESET`
- `CS[1:0]` or one-hot chip selects

Optional status back to the Mega:

- `BUSY`
- `DONE`
- `IRQ_PENDING`
- `READ_DATA_READY`

This lets the Mega load cycle parameters in several byte writes:

1. write ISA address low byte
2. write ISA address mid byte
3. write ISA address high nibble / flags
4. write write-data byte
5. write cycle-control register
6. pulse `START`

That is slower than presenting a full 16-bit parallel bus, but ISA cycles are slow enough that this is usually a fine trade.

## Why not use the Mega's full draft parallel bus?

Your current Mega pinout draft implies:

- `16` address signals
- `16` data signals
- command bits
- status bits
- control strobes

That is reasonable if the Mega were directly acting as a wide external bus master.

But for three CPLDs that also need to:

- drive ISA address lines
- handle ISA data direction
- sequence `IOR#`, `IOW#`, `MEMR#`, `MEMW#`
- collect IRQs
- possibly handle wait states / ready

the wide host-side bus burns pins without buying much.

The narrower register interface is a better pin trade.

## Functional split across 3 CPLDs

The cleanest split is by **function**, not strictly "one gets address, one gets data".

That is because:

- the control PLD needs to know cycle type and sometimes address class
- the data PLD needs direction and cycle phase
- the IRQ/status PLD needs to feed the control path

So the split should be:

- `isa_ctrl`: cycle FSM, strobes, reset, bus timing
- `data_path`: ISA data bus direction and data registers
- `irq_decode`: IRQ collection, optional status mux, optional extra address/control helpers

## Draft pin allocation

### CPLD 1: `isa_ctrl`

Primary job:

- sequence ISA I/O and memory cycles
- generate strobes and handshake
- expose control/status registers to the Mega

Likely signals:

- from Mega shared local interface:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `START`
  - `RESET`
  - `CS_ISACTRL`
- to Mega:
  - `BUSY`
  - `DONE`
- to ISA/backplane:
  - `IOR#`
  - `IOW#`
  - `MEMR#`
  - `MEMW#`
  - `AEN`
  - `BALE`
  - `RESETDRV`
  - optional `IOCHRDY` sample
  - optional `IOCS16#` sample
  - optional `MEMCS16#` sample
- to other CPLDs:
  - `cycle_active`
  - `cycle_dir`
  - `cycle_is_io`
  - `cycle_is_mem`
  - `sample_read`
  - `load_write_data`

Approximate external pin budget:

- around `15-20` Mega-side pins if fully local-bus-visible
- around `10-14` ISA/control/inter-CPLD pins

This is comfortable in a `64 I/O` package.

### CPLD 2: `data_path`

Primary job:

- hold the write-data byte from the Mega
- capture read-data byte from ISA
- control the ISA data bus direction
- optionally grow to `16-bit` ISA data later

Likely signals:

- from Mega shared local interface:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_DATAPATH`
- to Mega:
  - local-bus readback onto `MD[7:0]`
  - optional `READ_DATA_READY`
- to ISA/backplane:
  - `SD[7:0]`
  - optional future `SD[15:8]`
  - optional `SBHE#`
- from `isa_ctrl`:
  - `cycle_active`
  - `cycle_dir`
  - `sample_read`
  - `load_write_data`

Approximate external pin budget for 8-bit ISA mode:

- Mega-side shared bus visible: `14-15`
- ISA data bus: `8`
- control/inter-CPLD: `4-6`

This is very comfortable.

Approximate budget if you later support full 16-bit ISA data:

- same Mega-side: `14-15`
- ISA data bus: `16`
- optional `SBHE#` and size controls: `1-3`
- control/inter-CPLD: `4-6`

Still plausible in one `64 I/O` package, but less roomy.

### CPLD 3: `irq_decode`

Primary job:

- collect IRQ lines
- provide interrupt status/mask logic
- optionally hold the upper ISA address bits or support decode glue

Likely signals:

- from Mega shared local interface:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_IRQ`
- to Mega:
  - `IRQ_PENDING`
  - optional `VECTOR_READY`
- from ISA/backplane:
  - selected IRQ inputs such as `IRQ2..IRQ7`, `IRQ10..IRQ15`
- optional additional signals:
  - `DRQ` inputs later
  - `DACK` status later
  - address decode helpers
  - wait-state policy bits

Approximate external pin budget:

- Mega-side shared bus visible: `14-15`
- ISA IRQ inputs: `6-12`, depending how many you bring in
- status/inter-CPLD: `2-4`

Also comfortable.

## Address handling recommendation

This is the part that most affects pin count.

Do **not** dedicate `SA[19:0]` plus `SD[15:0]` plus a wide Mega-side address/data bus all at once.

Instead:

- Mega writes ISA address bytes into CPLD registers
- one CPLD latches and drives the ISA address bus during the cycle
- only the ISA-facing side needs the wide address bus physically present

For example:

- register `ADDR0` = `SA[7:0]`
- register `ADDR1` = `SA[15:8]`
- register `ADDR2` = `SA[19:16]` plus flags

That means the Mega only needs an `8-bit` local bus, not `20` dedicated address pins into the CPLDs.

## Data handling recommendation

Same idea for data:

- Mega writes the data byte into a `WRITE_DATA` register
- `data_path` CPLD drives `SD[7:0]` only during write cycles
- on read cycles, `data_path` samples `SD[7:0]` and makes it readable back to the Mega

So yes, **one device can principally own the data path**, but it still needs control signals from the control PLD.

## Initial ISA scope recommendation

Start with **8-bit ISA cycles only**.

Reasons:

- your known floppy card is `8-bit ISA`
- many VGA cards can still respond to 8-bit I/O register accesses even if video memory use is more complicated
- it cuts the early pin budget and logic complexity substantially
- it gets you to a working control plane sooner

That means your first-pass ISA-facing buses can be:

- `SA[19:0]`
- `SD[7:0]`
- `IOR#`
- `IOW#`
- `MEMR#`
- `MEMW#`
- `AEN`
- `BALE`
- `RESETDRV`
- selected `IRQ` lines

Then add:

- `SD[15:8]`
- `SBHE#`
- `IOCS16#`
- `MEMCS16#`

only if and when the software and card mix really need them.

## Suggested register map shape

This is one practical way to organize the shared local interface.

### `isa_ctrl`

- `0x0` `CTRL`
- `0x1` `STATUS`
- `0x2` `CYCLE_TYPE`
- `0x3` `TIMING`
- `0x4` `RESET_CONTROL`

### `data_path`

- `0x0` `WRITE_DATA_LO`
- `0x1` `READ_DATA_LO`
- `0x2` `DATA_FLAGS`
- `0x3` optional `WRITE_DATA_HI`
- `0x4` optional `READ_DATA_HI`

### `irq_decode`

- `0x0` `IRQ_STATUS_LO`
- `0x1` `IRQ_MASK_LO`
- `0x2` `IRQ_STATUS_HI`
- `0x3` `IRQ_MASK_HI`
- `0x4` `EVENT_FLAGS`

### optional `addr_path` behavior

You may end up implementing the address registers in either `isa_ctrl` or `irq_decode`, depending on which chip has more spare pins and logic.

A simple set would be:

- `0x8` `ADDR0`
- `0x9` `ADDR1`
- `0xA` `ADDR2`

## Practical conclusion

Your instinct is right:

- a single PLD handling full `16-bit in + 16-bit out + control` is asking too much
- spreading the work across `3` CPLDs is sensible

But the best spread is not:

- one PLD for all address
- one PLD for all data
- one PLD for everything else

The better first draft is:

- one for cycle control
- one for the data bus
- one for IRQ/status and spare decode glue

And the most important architectural change is:

- **replace the Mega's implied wide parallel CPLD interface with an 8-bit shared local register bus**

That gives you a much more believable schematic starting point.

## 4-CPLD option

If you are willing to grow from `3` to `4` `ATF1504AS` devices, the design space opens up in a useful way.

Your suggested split:

- one PLD for `8` address outputs
- one PLD for upper address outputs plus segment register support
- one PLD for `8` data in / `8` data out behavior
- one PLD for cycle control and IRQ glue

is much more realistic than trying to squeeze too much bidirectional bus ownership into a single device.

### Why 4 parts helps

The real pressure is not just raw pin count. It is the combination of:

- ISA-facing pins
- Mega-facing pins
- inter-CPLD coordination pins
- logic product-term pressure from timing and decode

Moving to `4` parts reduces both:

- pin crowding
- logic crowding inside each CPLD

That second point matters because even if the pin count fits, the cycle-control and mux logic can still become unpleasantly dense in a `64-macrocell` part.

### Recommended 4-way split

If you use four devices, I would recommend this function split:

1. `addr_lo`
2. `addr_hi`
3. `data_path`
4. `isa_ctrl_irq`

### `addr_lo`

Primary job:

- hold and drive `SA[7:0]`

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_ADDR_LO`
- to ISA:
  - `SA[7:0]`
- optional:
  - local readback of address latch

This PLD is very comfortable.

### `addr_hi`

Primary job:

- hold and drive `SA[15:8]`
- hold upper address / segment information
- optionally generate `SA[19:16]` from a small segment/page register

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_ADDR_HI`
- to ISA:
  - `SA[15:8]`
  - `SA[19:16]`
- optional:
  - readback of segment register
  - simple range-decode flags to control PLD

This is a nice home for the segment register idea.

### `data_path`

Primary job:

- latch Mega write data
- sample ISA read data
- control data direction

Recommended first pass:

- support `SD[7:0]` only
- keep `16-bit` ISA data as a future enhancement

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_DATA`
- to/from ISA:
  - `SD[7:0]`
- from control PLD:
  - `cycle_dir`
  - `sample_read`
  - `drive_write`
  - `cycle_active`

If you eventually need full `16-bit` ISA data, this is the PLD most likely to become crowded again.

### `isa_ctrl_irq`

Primary job:

- sequence ISA bus timing
- drive strobes
- watch ready / width / IRQ lines
- report status to Mega

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_CTRL`
  - `START`
  - `RESET`
- to Mega:
  - `BUSY`
  - `DONE`
  - `IRQ_PENDING`
- to ISA:
  - `IOR#`
  - `IOW#`
  - `MEMR#`
  - `MEMW#`
  - `BALE`
  - `AEN`
  - `RESETDRV`
- from ISA:
  - selected IRQ lines
  - optional `IOCHRDY`
  - optional `IOCS16#`
  - optional `MEMCS16#`
- to other CPLDs:
  - `cycle_active`
  - `cycle_is_io`
  - `cycle_is_mem`
  - `cycle_dir`
  - `sample_read`
  - `drive_write`

This is probably the best use of the fourth PLD budget.

## Important caution about "8-in 8-out"

This model is directionally right, but there is one subtle point:

the ISA data path is not really "`8-in` plus `8-out`" as two unrelated sets.

It is one shared bidirectional external bus:

- write cycle: CPLD drives `SD[7:0]`
- read cycle: CPLD samples `SD[7:0]`

So the data PLD still needs:

- `8` ISA data pins
- Mega-side local-bus visibility
- internal latches / muxing
- direction control

The fourth PLD helps a lot, but it does not eliminate the need for careful bus-direction design.

## Does 4 PLDs justify a wide Mega interface?

Still no.

Even with four CPLDs, I would keep the Mega-to-CPLD side as a narrow shared register bus.

Reasons:

- simpler routing
- fewer Mega pins consumed
- easier CPLD pin budgeting
- more flexible internal register model
- cleaner future change path if the Mega is later replaced

So the extra PLD should buy you:

- cleaner partitioning
- more ISA-facing resources
- easier timing and decode logic

not a return to a full-width host-side parallel bus.

## Hardware/firmware staging recommendation

The best compromise for this project is:

- wire the hardware for full `16-bit ISA`
- keep the Mega-to-CPLD side as an `8-bit` shared local register bus
- start with firmware that only performs `8-bit` ISA cycles
- enable `16-bit` firmware transactions later once the control plane is stable

This gives you the right physical capability without forcing rev-A firmware to solve every width-related problem immediately.

### What "wired for 16-bit" means

Include in the schematic from the beginning:

- `SA[19:0]`
- `SD[15:0]`
- `SBHE#`
- `IOR#`
- `IOW#`
- `MEMR#`
- `MEMW#`
- `AEN`
- `BALE`
- `RESETDRV`
- `IOCS16#`
- `MEMCS16#`
- selected `IRQ` lines

### What "8-bit firmware first" means

The initial firmware and CPLD micro-architecture can deliberately restrict themselves to:

- only driving and sampling `SD[7:0]`
- only issuing byte-wide I/O and memory cycles
- treating `SD[15:8]` and `SBHE#` as provisioned-but-unused
- possibly observing `IOCS16#` / `MEMCS16#` for diagnostics without acting on them yet

That makes bring-up much more manageable while preserving your option to grow into full-width operation without a board respin.

## Revised 4-way split for 16-bit-capable hardware

With the board wired for 16-bit ISA, I would still keep the four-way split, but I would tighten the role of the `data_path` PLD and accept that one of the address/control PLDs may assist with upper-byte data support later if needed.

### `addr_lo`

Primary job:

- hold and drive `SA[7:0]`

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_ADDR_LO`
- to ISA:
  - `SA[7:0]`

### `addr_hi`

Primary job:

- hold and drive `SA[15:8]`
- hold `SA[19:16]`
- hold segment/page register
- optionally assist with byte-lane / width policy glue

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_ADDR_HI`
- to ISA:
  - `SA[15:8]`
  - `SA[19:16]`
- optional to/from control/data PLDs:
  - width/segment/decode helper signals

### `data_path`

Primary job:

- own the low data byte from day one
- provide the framework for full `SD[15:0]` support later

Recommended implementation stages:

1. rev-A hardware:
   - wire `SD[15:0]`
   - include `SBHE#`
2. initial firmware/CPLD image:
   - actively use only `SD[7:0]`
3. later firmware/CPLD image:
   - add upper-byte and word-cycle support

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_DATA`
- to/from ISA:
  - `SD[7:0]`
  - provision for `SD[15:8]`
  - `SBHE#`
- from control PLD:
  - `cycle_dir`
  - `sample_read`
  - `drive_write`
  - `cycle_active`
  - width-select / byte-lane control

### `isa_ctrl_irq`

Primary job:

- sequence ISA timing
- manage 8/16-bit cycle policy
- watch width-response signals
- collect IRQs

Signals:

- from Mega local bus:
  - `MD[7:0]`
  - `RA[3:0]`
  - `RD#`
  - `WR#`
  - `CS_CTRL`
  - `START`
  - `RESET`
- to Mega:
  - `BUSY`
  - `DONE`
  - `IRQ_PENDING`
  - optional width/status flags
- to ISA:
  - `IOR#`
  - `IOW#`
  - `MEMR#`
  - `MEMW#`
  - `BALE`
  - `AEN`
  - `RESETDRV`
- from ISA:
  - `IOCHRDY`
  - `IOCS16#`
  - `MEMCS16#`
  - selected IRQ lines
- to other CPLDs:
  - `cycle_active`
  - `cycle_is_io`
  - `cycle_is_mem`
  - `cycle_dir`
  - `sample_read`
  - `drive_write`
  - width / lane control

## Register-level implication

If you wire for 16-bit now, define the register model with word support from the start even if rev-A firmware only uses the low byte.

For example:

- `WRITE_DATA_LO`
- `WRITE_DATA_HI`
- `READ_DATA_LO`
- `READ_DATA_HI`
- `ADDR0`
- `ADDR1`
- `ADDR2`
- cycle-width flags in `CTRL` or `CYCLE_TYPE`

That way the software model does not need a major redesign later.

## Reserving a future 16-bit Mega/CPLD local bus

If you want the option of widening the Mega-to-CPLD local bus later, the clean approach is:

- keep rev-A operation at `8-bit`
- explicitly reserve a contiguous high-byte path on the Mega
- avoid burning the corresponding CPLD spare I/O on unrelated functions

Recommended reservation policy:

- active local bus now: `MD[7:0]`
- reserve future local high byte: `MD[15:8]`
- reserve a few sideband/control lines for width and lane policy

This preserves the upgrade path without paying the full complexity cost in the first firmware and CPLD image.

See also:

- `C:\Users\pdr0663\PDR-16_AT\MEGA Pinouts.local_bus_reserved_16.csv`
- `C:\Users\pdr0663\PDR-16_AT\docs\architecture\mega_cpld_local_bus_reservations.md`

## My recommendation

If board area and power are acceptable, `4` CPLDs is a good move.

For a first draft schematic, I would now target:

- `4` `ATF1504AS`
- `8-bit` Mega local register bus
- full `20-bit` ISA address bus in hardware
- full `16-bit` ISA data bus in hardware
- `SBHE#`, `IOCS16#`, and `MEMCS16#` wired from the start
- segment/page register in `addr_hi`
- initial firmware restricted to `8-bit` cycles

That gives you a realistic rev-A bring-up path without painting the hardware into an `8-bit` corner.
