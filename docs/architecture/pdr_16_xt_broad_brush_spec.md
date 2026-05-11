# PDR-16/XT Broad-Brush Specification

## 1. Project Identity

**Project name:** PDR-16/XT  
**Project identifier:** `PDR-16_XT`

PDR-16/XT is a 16-bit word-oriented Forth machine using an ATmega2560 as the current execution engine, two ATF1504AS CPLDs as deterministic bus/interface logic, and an XT-class 8-bit ISA expansion bus for period-correct peripheral cards.

The machine is not intended to be an IBM PC clone. It is a native PDR/Forth architecture that speaks enough 8-bit ISA bus protocol to use selected XT-compatible or XT-tolerant cards.

## 2. Design Philosophy

The design should preserve the character of the original PDR-16:

- 16-bit word-oriented architecture
- native Forth execution model
- segmented memory model
- simple, inspectable hardware
- incremental construction and testing
- strong separation between CPU architecture and peripheral bus details

The current implementation uses an ATmega2560 as a microcode/VM execution engine. A future FPGA or custom datapath could still replace the ATmega without invalidating the virtual machine architecture, Forth software model, or ISA bus interface, but the external bus target remains XT-class 8-bit ISA.

## 3. Implementation Layers

```text
Forth system / monitor / tools
        ->
PDR-16/XT virtual machine
        ->
ATmega2560 execution engine
        ->
Two-PLD ISA bus processor
        ->
8-bit ISA-compatible peripheral bus
        ->
VGA card, floppy controller, other cards
```

## 4. Core Hardware Platform

### 4.1 CPU / Execution Engine

The first implementation uses an Arduino Mega board fitted with an ATmega2560.

The ATmega2560 is not considered the final architectural CPU. It is the current execution substrate for the abstract PDR-16/XT machine.

Responsibilities:

- execute the PDR-16/XT VM
- host the initial Forth kernel
- provide bootstrap and diagnostic firmware
- command CPLD-managed ISA bus cycles
- manage internal stacks and machine state initially
- provide USB serial diagnostics during development

### 4.2 CPLD Logic

The current hardware target uses exactly two `ATF1504AS` devices.

Suggested split:

- `isa_ctrl_addr`
  - cycle sequencing
  - address/control generation
  - Mega handshake/status
  - ISA reset and optional IRQ sampling
- `isa_data_irq`
  - `SD[7:0]` data path
  - read/write data latches
  - data direction control
  - IRQ/status aggregation

The CPLDs form a timing firewall between the relatively flexible ATmega side and the stricter ISA bus side.

### 4.3 Construction Strategy

Initial physical design may use:

- modified Arduino Mega with downward-facing headers
- ISA prototyping backplane or passive slot backplane
- custom CPLD daughter-board near the ISA connector
- wire-wrap between Mega and CPLD board
- PCB routing for the critical CPLD-to-ISA bus section

Preferred split:

```text
Mega -> CPLDs: experimental, wire-wrapped, slow handshake interface
CPLDs -> ISA: short, clean, PCB-routed bus interface
```

## 5. Bus Strategy

### 5.1 External Bus Scope

The external bus target is an XT-class 8-bit ISA subset.

This means the design intentionally excludes:

- `SD8-SD15`
- `SBHE#`
- `IOCS16#`
- `MEMCS16#`
- 16-bit byte-lane steering
- 16-bit memory or I/O cycles

The internal machine remains 16-bit word-oriented. The external peripheral bus is permanently 8-bit.

### 5.2 Initial ISA Signals

Initial support should include at least:

```text
SA0-SA19
SD0-SD7
IOR#
IOW#
MEMR#
MEMW#
BALE
RESETDRV
AEN held inactive
selected IRQ inputs, optional at first
```

Intentionally omitted:

```text
SD8-SD15
SBHE#
IOCS16#
MEMCS16#
DMA DRQ/DACK lines
MASTER#
REFRESH#
bus mastering
```

## 6. ATmega-to-CPLD Interface

The ATmega should not bit-bang ISA bus timing directly. Instead, it commands the CPLD pair through a narrow register-style interface.

Basic transaction model:

```text
1. ATmega presents address, data, and command fields.
2. ATmega asserts START.
3. CPLDs latch the request.
4. CPLDs perform the ISA bus cycle.
5. CPLDs return DONE/BUSY/status.
6. ATmega samples data/status if required.
7. ATmega deasserts START.
```

Prefer level-sensitive handshakes over narrow pulses.

Possible register-style interface:

```text
ADDR_LO
ADDR_HI
ADDR_EXT / segment or page field
DATA_LO
COMMAND
STATUS
START / DONE / BUSY
```

The Mega side can be relatively slow and forgiving. The CPLD-to-ISA side should generate clean, deterministic strobes.

## 7. Timing Philosophy

The system should prioritise reliability and debuggability over speed.

Initial bus cycles may be slower than original XT-era cycles. Once reliable operation is established, timings can be tightened within the limits of the fixed 8-bit design.

## 8. Memory Model

PDR-16/XT remains a 16-bit word machine.

Likely model:

```text
segment: 16 bits
offset:  16 bits, word addressed
word:    16 bits
```

The ISA bus remains byte-addressed. The bridge or VM must explicitly translate between PDR word addresses and ISA byte addresses.

Possible physical address rule:

```text
physical_byte_address = segment_base + offset * 2
```

## 9. Initial Memory Resources

Initial firmware may use:

- ATmega flash for VM firmware and bootstrap code
- ATmega SRAM for stacks, registers, small buffers, and VM state
- ATmega EEPROM for small persistent configuration if useful

The ATmega2560 SRAM is limited, so larger Forth dictionary storage may eventually require external memory, but the ISA bus interface remains 8-bit.

## 10. Storage

### 10.1 Initial Storage Target

The initial storage target is an 8-bit ISA floppy disk controller card based on the Western Digital WD37C65BJM or similar, connected to a GoTek floppy emulator.

This provides:

- period-appropriate removable storage
- low data rate
- command-oriented controller behaviour
- PC-readable disk images
- easy exchange of files between PDR-16/XT and other systems

### 10.2 Initial Storage Mode

Initial operation should avoid DMA and may also avoid interrupts.

Preferred early mode:

```text
programmed I/O
polling
single-sector read/write operations
FAT-compatible filesystem layer above raw sectors
```

## 11. Video

The initial video target is a Trident TVGA9000B ISA VGA card.

The card is expected to be jumper-era hardware and likely capable of 8-bit or XT-compatible operation, subject to confirmation.

Initial video goal:

```text
80x25 VGA text mode
```

The first success criterion is direct screen output, not graphics performance.

The machine need not execute VGA BIOS code. VGA initialisation should be performed directly by PDR-16/XT software or by initial diagnostic firmware.

## 12. Keyboard and Console

Initial console may be via the Arduino Mega USB serial connection.

Later keyboard options include:

- PS/2 keyboard interface via microcontroller or CPLD
- USB keyboard through auxiliary controller
- ISA multi-I/O card if practical
- serial terminal as permanent fallback

The first system should not depend on an AT keyboard controller.

## 13. Interrupts And DMA

Interrupt support is optional initially. Early system operation may be polling-based.

DMA is explicitly deferred. The first PDR-16/XT should not implement ISA DMA.

This means some ISA peripherals may be unusable initially, or must be operated in programmed I/O modes.

## 14. Software Architecture

The PDR-16/XT architecture should be specified as a virtual machine independent of the ATmega implementation.

The ATmega firmware implements this VM.

The native software environment is Forth-like or Forth-derived, with device words for ISA I/O, storage, and diagnostics.

## 15. Development Milestones

### Milestone 0: Repository and documentation

- create `PDR-16_XT` project structure
- document VM assumptions
- document bus transaction model
- document Mega pin assignments
- document the fixed two-PLD partition

### Milestone 1: Mega diagnostics

- direct port access tests
- serial monitor diagnostics
- LED heartbeat
- basic command shell

### Milestone 2: CPLD handshake

- Mega writes command/data/address to CPLDs
- CPLDs report DONE/BUSY
- no ISA card required
- logic analyser verifies handshake

### Milestone 3: Fake ISA cycle

- CPLDs generate ISA-style timing into test pins
- verify BALE, IOR#, IOW#, MEMR#, MEMW# timing
- verify transceiver control strategy

### Milestone 4: ISA I/O read/write

- connect to ISA slot/card
- perform basic I/O read/write cycles
- read VGA status register if possible

### Milestone 5: VGA proof of life

- initialise or access VGA text mode
- write characters to display
- achieve `PDR-16/XT` screen output

### Milestone 6: Floppy controller proof of life

- read controller status
- reset controller
- issue basic commands
- communicate with GoTek emulator

### Milestone 7: FAT floppy filesystem

- sector read/write
- parse FAT12 boot sector / BPB
- read root directory
- open and read 8.3 files
- implement source/module loading from FAT files

### Milestone 8: Native PDR-16/XT environment

- Forth prompt on VGA or serial
- FAT floppy storage usable
- basic editor/monitor
- self-hosting experiments

## 16. Deferred Features

The following are explicitly deferred:

- FPGA CPU implementation
- ISA DMA
- bus mastering
- PC BIOS compatibility
- IDE hard disk support
- USB support
- advanced graphics modes
- multitasking
- full interrupt controller

## 17. Guiding Principle

PDR-16/XT is not a PC clone.

It is a PDR/Forth-native 16-bit word machine that uses selected XT-class ISA cards as intelligent peripherals.

The architecture should remain simple, inspectable, and evolvable without pretending to be a future 16-bit AT bus design.
