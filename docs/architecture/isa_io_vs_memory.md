# ISA I/O cycles vs memory cycles

## Core idea

On ISA, a bus transfer is identified by three things:

- the address on the address lines
- the control strobes
- the data on the data bus

The card watches the bus and decides whether the current cycle is meant for it.

## Two main cycle types

### I/O cycle

Used to access peripheral registers.

Typical strobes:

- `IOR#` for I/O read
- `IOW#` for I/O write

Meaning:

- "talk to a register inside a peripheral card"

Examples:

- floppy controller ports at `0x3F0` to `0x3F7`
- VGA control ports such as `0x3D4` and `0x3D5`

### Memory cycle

Used to access memory locations.

Typical strobes:

- `MEMR#` for memory read
- `MEMW#` for memory write

Meaning:

- "talk to a memory location on a RAM, ROM, or memory-mapped device"

Examples:

- RAM expansion card memory
- VGA display memory such as text or graphics framebuffer regions

## Common bus pattern

Both cycle types follow the same broad pattern:

1. the bus master places an address on the address lines
2. the bus master asserts the appropriate read or write strobe
3. a card that recognizes the cycle responds
4. data moves on the data bus

The main difference is the meaning of the address and which strobe is active.

## Floppy controller example: I/O write

Suppose the bus master writes to floppy controller port `0x3F2`.

What happens:

1. address `0x3F2` appears on the ISA address lines
2. `IOW#` is asserted
3. the floppy controller decodes that port and recognizes it
4. the bus master drives `SD[7:0]`
5. the floppy controller latches the byte

Interpretation:

- the address selects which floppy register is being written
- the byte on the data bus is the value for that register

So the port address is not an "instruction" by itself. It is a register selector.

## Floppy controller example: I/O read

Suppose the bus master reads from floppy controller port `0x3F4`.

What happens:

1. address `0x3F4` appears on the ISA address lines
2. `IOR#` is asserted
3. the floppy controller decodes that port and recognizes it
4. the floppy controller drives `SD[7:0]`
5. the bus master samples the returned byte

Interpretation:

- the selected port corresponds to a status or data register
- the card returns the current value of that register

## VGA example: I/O register access

Many VGA control registers are accessed through I/O ports.

One common indexed-register pattern is:

1. write an internal register number to index port `0x3D4`
2. write or read the associated value through data port `0x3D5`

This means:

- the ISA port address selects the VGA register gateway
- the value written to that port selects which internal VGA register you want
- the next access transfers the actual register value

So some cards use:

- direct register ports

and some use:

- indexed register ports

## VGA example: memory access

VGA also exposes display memory through memory cycles.

For example, in text mode or graphics mode, the bus master may access a display-memory region such as `0xB8000` or `0xA0000`, depending on mode.

What happens on a VGA memory write:

1. the bus master places the target memory address on the ISA address lines
2. `MEMW#` is asserted
3. the VGA card decodes the address range
4. the bus master drives the data bus
5. the VGA card stores that byte or word into display memory

What happens on a VGA memory read:

1. the bus master places the target memory address on the ISA address lines
2. `MEMR#` is asserted
3. the VGA card decodes the address range
4. the VGA card drives the data bus
5. the bus master samples the returned data

## Why this matters for PDR-16/XT

Your ISA interface should model at least these fields for each bus transaction:

- cycle type: `I/O` or `memory`
- direction: `read` or `write`
- width: `8-bit`
- address
- write data or read data

That is enough to describe:

- floppy control register accesses
- VGA register programming
- VGA memory access
- RAM/ROM expansion access

## Useful mental model

- I/O cycle: "which peripheral register?"
- memory cycle: "which memory location?"
- read strobe: "card drives the data bus"
- write strobe: "bus master drives the data bus"

## Practical bring-up implication

An `8-bit` first implementation is still very useful because:

- floppy control is fundamentally register-oriented and byte-friendly
- VGA control registers are mostly byte-oriented
- even VGA text memory can be accessed a byte at a time during bring-up

For PDR-16/XT, `8-bit` access is not just a bring-up shortcut; it is the intended permanent external-bus mode.
