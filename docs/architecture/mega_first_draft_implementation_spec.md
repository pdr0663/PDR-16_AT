# PDR-16/XT MEGA First-Draft Implementation Specification

## 1. Purpose

This document defines the first runnable `PDR-16/XT` implementation on the Arduino Mega 2560.

The goal of this draft is:

- boot a native Forth system on the MEGA
- use the MEGA main serial port as the only console interface
- preserve the V5 Forth-visible execution model where practical
- avoid ISA peripherals for the first bring-up
- avoid host-backed file services
- create the first runnable bring-up platform for the fixed `PDR-16/XT` machine

This is a bring-up implementation, not the final architecture.

## 2. Non-goals

The first draft does **not** attempt to implement:

- ISA memory
- ISA I/O devices
- floppy or file I/O
- VGA
- packetized host-terminal transport
- cycle-accurate V5 microcode emulation
- exact V5 ROM binary compatibility

The only compatibility surface that must be preserved is the Forth-visible machine behavior required to boot and use the system interactively.

## 3. Architectural Position

The MEGA firmware is an implementation of the `PDR-16/XT` virtual machine, not the final CPU architecture.

The first draft uses:

- Python tooling to build the seeded Forth ROM image
- MEGA firmware to execute that image
- C-like Arduino code for the runtime

The VM implementation itself is not part of the Forth-visible memory map.

## 4. High-Level Model

The machine remains a:

- `16-bit`
- word-addressed
- threaded Forth machine

Execution cells in memory are interpreted as follows:

- `0..63`:
  - primitive opcodes
- `64..65535`:
  - execution tokens into threaded Forth words

This preserves the V5 tagged execution model while allowing a more direct and efficient MEGA implementation.

## 5. Execution Strategy

### 5.1 Primitive dispatch

The firmware shall implement a primitive dispatch table with `64` entries:

```c
void (*primitive_table[64])(void);
```

Each entry maps directly to one Forth primitive opcode.

When the interpreter fetches a cell:

- if the cell value is less than `64`, dispatch through `primitive_table[cell]`
- otherwise treat the value as a colon-word execution token

### 5.2 Colon-word execution

Colon words shall be executed as threaded code.

Conceptually:

- an execution token identifies a Forth word body
- entering a colon word performs the logical equivalent of `doLIST`
- the return address is saved on the return stack
- `IP` advances through the word body until `EXIT`

### 5.3 Internal machine model

The firmware does **not** need to emulate the V5 microarchitecture literally.

It should preserve only the required Forth-visible behavior.

A recommended internal state model is:

- `IP`
- `SP`
- `RP`
- cached `TOS`
- optional cached return-top if useful
- memory backend state
- primitive-local scratch state as needed

The implementation may use a simplified stack model as long as all primitives are internally consistent and Forth behavior remains correct.

## 6. Firmware Language Style

The firmware shall be written in a C-like subset suitable for the Arduino IDE.

Preferred style:

- plain structs
- plain functions
- arrays
- enums / `#define`
- explicit integer types
- minimal C++ syntax only where required by the Arduino toolchain

Avoid:

- classes
- templates
- exceptions
- complex C++ abstractions

## 7. Memory Model

### 7.1 Forth-visible address space

The first draft presents the normal `segment 0` logical address space only.

The visible address space remains:

- `0x0000 .. 0xFFFF` words

### 7.2 Draft segment 0 layout

The initial MEGA draft uses the existing V5-style logical split:

- `0x0000 .. 0x7FFF`
  - ROM-like image
  - flash-backed
- `0x8000 .. 0xFFFF`
  - logical RAM space

This retains the important Forth assumption that:

- the runtime dictionary begins at the bottom of RAM
- the working set lives toward the top of memory

### 7.3 Logical RAM policy

The logical RAM half shall be treated as a VM-defined space backed by scarce MEGA SRAM.

The implementation shall prioritize backing:

- top-of-memory working set
- low-RAM dictionary growth from `0x8000` upward

Any unimplemented logical RAM gap may be:

- unmapped
- trap-filled
- or backed by a minimal scratch region if later needed

For the first draft, unmapped behavior is preferred unless a concrete compatibility issue requires otherwise.

## 8. Current Draft Runtime Layout

The copied Forth build currently uses these important runtime addresses:

- `CP_START = 0x8000`
- `SP0_INIT = 0xF97F`
- `RP0_INIT = 0xFE7F`
- `TIBB = 0xFB00`
- `EVALB = 0xFA80`
- `SPP = 0xF980`
- `RPP = 0xFE80`
- `UPP = 0xFE80`

These values come from the current copied toolchain after halving the stack reservations.

### 8.1 Stack reductions

For the first MEGA draft:

- data stack size is halved from the V5 reference value
- return stack size is halved from the V5 reference value

This is a deliberate SRAM-saving measure for bring-up.

### 8.2 Dictionary growth

The dictionary pointer `CP` shall be initialized to the bottom of RAM:

- `0x8000`

New words are therefore built upward from the bottom of logical RAM.

This behavior is required and shall be preserved.

## 9. ROM Image Build Strategy

### 9.1 Source of truth

The seeded Forth system shall continue to be built by Python tooling.

The Python build remains the source of truth for:

- ROM image contents
- dictionary layout
- seeded user variables
- Forth source inclusion
- primitive metadata

### 9.2 Reason for keeping Python

The Python tooling already captures the required seeded-image behavior and is easier to maintain than rewriting the metacompiler in C.

Therefore the MEGA firmware shall consume generated artifacts rather than recreate the seed image itself.

### 9.3 Export artifact

The build process shall export an Arduino-consumable ROM header:

- `firmware/mega/pdr_vm/generated/pdr16_xt_forth_image.h`

This header contains:

- a `PROGMEM` word array
- a ROM word count constant

## 10. Console I/O Model

### 10.1 Console transport

The first draft uses only the MEGA principal serial port for console I/O.

Console transport is:

- plain serial byte input
- plain serial byte output

No packet framing is required.

### 10.2 Required primitive surface

The following primitive-facing behaviors are required:

- `?rx`
  - report whether a byte is available
  - when available, return the byte and true
  - otherwise return false
- `tx!`
  - transmit one byte

### 10.3 Forth-facing console words

The copied seed currently binds:

- `?KEY -> ?rx`
- `EMIT -> tx!`
- `EXPECT -> accept`

This simple binding is appropriate for the first draft and shall be retained unless an audit later identifies a correction.

### 10.4 No host file service

The V5 packetized host-terminal and host-backed file services are explicitly excluded from the MEGA draft.

Later file and storage operations will be implemented through ISA devices, not the serial console link.

## 11. Primitive Semantics

### 11.1 Compatibility rule

Primitive implementations shall preserve the required Forth behavior, not the internal V5 micro-operations.

### 11.2 Implementation rule

Each primitive should be implemented directly in firmware in the most efficient clear way available on the MEGA.

Examples:

- stack primitives operate directly on cached state and memory
- arithmetic primitives operate directly on machine words
- control-flow primitives update `IP` and the return stack directly
- memory primitives use the VM memory backend

### 11.3 Priority for initial bring-up

Initial bring-up shall focus on the primitives needed for:

- cold boot
- text interpretation
- serial console I/O
- basic arithmetic and control flow
- dictionary growth

Host file primitives may remain stubbed or unimplemented in the MEGA firmware until ISA-backed storage exists.

## 12. Memory Backend Requirements

The firmware shall provide helper functions equivalent in spirit to:

```c
uint16_t vm_read_word(uint16_t addr);
void vm_write_word(uint16_t addr, uint16_t value);
uint8_t vm_read_byte(uint16_t addr);
void vm_write_byte(uint16_t addr, uint8_t value);
```

These helpers shall hide the fact that the logical Forth memory space is backed by mixed physical storage.

### 12.1 ROM region

For `0x0000 .. 0x7FFF`:

- reads come from flash / `PROGMEM`
- writes are rejected or ignored

### 12.2 RAM region

For logical RAM addresses:

- reads and writes are serviced by the MEGA runtime memory backend
- the implementation may use address translation internally

## 13. Recommended Firmware Structure

A recommended layout is:

- `machine_state_t`
  - interpreter state
- `vm_memory.c` / equivalent
  - memory backend
- `vm_primitives.c` / equivalent
  - primitive implementations
- `vm_dispatch.c` / equivalent
  - fetch / execute loop
- `vm_serial.c` / equivalent
  - console UART support
- generated ROM header
  - built by Python tooling

Actual filenames may vary to suit the Arduino build environment.

## 14. Bring-Up Sequence

Recommended first bring-up order:

1. load generated ROM image into firmware build
2. implement memory read path for ROM
3. implement minimal logical RAM backend
4. implement serial `?rx` and `tx!`
5. implement primitive table and fetch loop
6. implement enough primitives to execute `COLD`
7. reach a serial Forth prompt
8. verify basic interaction:
   - stack ops
   - arithmetic
   - dictionary growth
   - defining and executing new words

## 15. Verification Goals

Success for this draft means:

- the system boots on the MEGA
- serial console interaction works
- a Forth prompt appears
- simple definitions can be entered
- new words compile into logical RAM starting at `0x8000`
- the reduced-stack memory layout remains stable during normal interactive use

## 16. Expected Future Changes

This draft is expected to evolve when ISA support is introduced.

Likely future changes include:

- backing more of logical RAM with external memory
- implementing file and storage words over ISA devices
- adding additional segments beyond `segment 0`
- introducing ISA I/O and memory windows
- refining or replacing the MEGA runtime core

These future changes should not invalidate the core Forth-visible model established by this draft.
