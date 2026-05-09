# PDR-16/AT Broad-Brush Specification

## 1. Project Identity

**Project name:** PDR-16/AT  
**Repository/folder name:** `PDR-16_AT`

PDR-16/AT is a 16-bit word-oriented Forth machine using an ATmega2560 as an initial execution engine, ATF1504AS CPLDs as deterministic bus/interface logic, and an ISA/PC-AT-compatible expansion bus for period-correct peripheral cards.

The machine is not intended to be an IBM PC clone. It is a native PDR/Forth architecture that speaks enough ISA bus protocol to use selected PC/AT peripheral cards.

## 2. Design Philosophy

The design should preserve the character of the original PDR-16:

- 16-bit word-oriented architecture
- native Forth execution model
- segmented memory model
- simple, inspectable hardware
- incremental construction and testing
- strong separation between CPU architecture and peripheral bus details

The initial implementation uses an ATmega2560 as a microcode/VM execution engine. A future FPGA or custom datapath should be able to replace the ATmega without invalidating the virtual machine architecture, Forth software model, or ISA bus interface.

## 3. Implementation Layers

```text
Forth system / monitor / tools
        ↓
PDR-16/AT virtual machine
        ↓
ATmega2560 execution engine
        ↓
ATF1504AS CPLD bus processor
        ↓
8-bit ISA-compatible peripheral bus
        ↓
VGA card, floppy controller, other cards
```

## 4. Core Hardware Platform

### 4.1 Initial CPU / Execution Engine

The first implementation uses an Arduino Mega board fitted with an ATmega2560.

The ATmega2560 is not considered the final architectural CPU. It is the first execution substrate for the abstract PDR-16/AT machine.

Responsibilities:

- execute the PDR-16/AT VM
- host the initial Forth kernel
- provide bootstrap and diagnostic firmware
- command CPLD-managed ISA bus cycles
- manage internal stacks and machine state initially
- provide USB serial diagnostics during development

### 4.2 CPLD Logic

The design uses multiple ATF1504AS CPLDs, likely three initially.

CPLD responsibilities:

- ISA bus cycle sequencing
- address/control signal generation
- data bus direction control
- byte-lane handling where required
- AVR-to-bus handshake logic
- ISA reset generation
- IRQ collection and status presentation
- optional future SRAM interface support

The CPLDs form a timing firewall between the relatively flexible ATmega side and the stricter ISA bus side.

### 4.3 Construction Strategy

Initial physical design may use:

- modified Arduino Mega with downward-facing headers
- PC/AT prototyping board
- custom CPLD daughter-board near the ISA connector
- wire-wrap between Mega and CPLD board
- PCB routing for the critical CPLD-to-ISA bus section

The preferred split is:

```text
Mega ↔ CPLDs: experimental, wire-wrapped, slow handshake interface
CPLDs ↔ ISA: short, clean, PCB-routed bus interface
```

## 5. Bus Strategy

### 5.1 Initial ISA Mode

The initial external bus target is an 8-bit ISA subset.

This deliberately avoids early complexity involving:

- SD8-SD15
- SBHE#
- IOCS16#
- MEMCS16#
- 16-bit byte-lane steering
- odd/even word access complications

The internal machine remains 16-bit word-oriented. The external bus may initially be 8-bit.

### 5.2 Future 16-bit Expansion

The design should leave room for later 16-bit ISA support.

Future support may include:

- SD8-SD15
- SBHE#
- 16-bit I/O cycles
- 16-bit memory cycles
- improved VGA memory throughput
- IDE or other 16-bit cards

The initial design should not block this expansion, but it need not implement it immediately.

### 5.3 ISA Signals Required Initially

Initial 8-bit bus support should include at least:

```text
SA0-SA19
SD0-SD7
IOR#
IOW#
MEMR#
MEMW#
BALE
RESETDRV
AEN held inactive unless DMA is later implemented
IRQ inputs, initially optional or polled
```

Initially omitted or deferred:

```text
SD8-SD15
SBHE#
IOCS16#
MEMCS16#
DMA DRQ/DACK lines
MASTER#
REFRESH#
advanced wait-state handling
bus mastering
```

## 6. ATmega-to-CPLD Interface

The ATmega should not bit-bang ISA bus timing directly. Instead, it commands the CPLD bus processor.

Basic transaction model:

```text
1. ATmega presents address, data, and command fields.
2. ATmega asserts START.
3. CPLD latches request.
4. CPLD performs ISA bus cycle.
5. CPLD returns DONE/BUSY/status.
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
DATA_HI
COMMAND
STATUS
START / DONE / BUSY
```

The ATmega side can be relatively slow and forgiving. The CPLD-to-ISA side should generate clean, deterministic strobes.

## 7. Timing Philosophy

The system should prioritise reliability and debuggability over speed.

Initial bus cycles may be slower than original PC/AT cycles. Once reliable operation is established, timings can be tightened.

Clock-like or strobe-like signals must be treated carefully:

```text
CPLD clock
START
DONE/BUSY
BALE
IOR#
IOW#
MEMR#
MEMW#
transceiver OE#/DIR
latch enables
RESETDRV
```

Settling signals are less critical if sampled only after adequate delay:

```text
address bus
data bus
command bits
status bits
IRQ levels
mode selects
```

## 8. Memory Model

The PDR-16/AT remains a 16-bit word machine.

A likely model is:

```text
segment: 16 bits
offset:  16 bits, word addressed
word:    16 bits
```

The ISA bus remains byte-addressed. The bridge or VM must explicitly translate between PDR word addresses and ISA byte addresses.

A possible physical address rule:

```text
physical_byte_address = segment_base + offset × 2
```

The exact segment mapping is to be defined later.

## 9. Initial Memory Resources

### 9.1 ATmega Internal Resources

Initial firmware may use:

- ATmega flash for VM firmware and bootstrap code
- ATmega SRAM for stacks, registers, small buffers, and VM state
- ATmega EEPROM for small persistent configuration if useful

The ATmega2560 SRAM is limited, so larger Forth dictionary storage may eventually require external memory.

### 9.2 Future External RAM

Possible later RAM options:

- SRAM managed through CPLD
- ISA memory card
- memory on a future custom board
- FPGA block RAM in later implementation

The first system should not depend on external RAM unless necessary.

## 10. Storage

### 10.1 Initial Storage Target

The initial storage target is an 8-bit ISA floppy disk controller card based on the Western Digital WD37C65BJM or similar, connected to a GoTek floppy emulator.

This provides:

- period-appropriate removable storage
- low data rate
- command-oriented controller behaviour
- PC-readable disk images
- easy exchange of files between PDR-16/AT and other systems

### 10.2 Initial Storage Mode

Initial operation should avoid DMA and possibly interrupts.

Preferred early mode:

```text
programmed I/O
polling
single-sector read/write operations
FAT-compatible filesystem layer above raw sectors
```

DMA and IRQ6 may be added later.

### 10.3 Filesystem Strategy

The preferred initial filesystem is FAT12 for floppy compatibility.

FAT12 is a natural target because it is the standard filesystem for classic DOS-format floppy disks and is appropriate for 720 KB, 1.2 MB, and 1.44 MB floppy images.

The PDR-16/AT should treat the floppy as a sector-addressed block device at the driver level, but should expose files rather than traditional Forth numbered blocks at the user level.

A minimal initial FAT implementation may support:

- reading the boot sector / BIOS Parameter Block
- locating FAT tables
- locating the root directory
- reading 8.3 filenames
- following FAT12 cluster chains
- opening and reading files
- eventually creating, writing, deleting, and renaming files

Long filenames, subdirectories, timestamps, and full DOS attribute semantics may be deferred.

The Forth system may still use its own internal source/module format, but those sources should live as ordinary FAT files rather than raw Forth blocks.

## 11. Video

### 11.1 Initial Video Target

The initial video target is a Trident TVGA9000B ISA VGA card.

The card is expected to be jumper-era hardware and likely capable of 8-bit or XT-compatible operation, subject to confirmation.

### 11.2 Initial Video Mode

Initial video goal:

```text
80×25 VGA text mode
```

The first success criterion is direct screen output, not graphics performance.

The machine need not execute VGA BIOS code. VGA initialisation should be performed directly by PDR-16/AT software or by initial diagnostic firmware.

### 11.3 Later Video Options

Later work may include:

- faster text output
- direct VGA memory access
- simple graphics modes
- PDR-native terminal driver
- editor/monitor interface

## 12. Keyboard and Console

Initial console may be via the Arduino Mega USB serial connection.

Later keyboard options include:

- PS/2 keyboard interface via microcontroller or CPLD
- USB keyboard through auxiliary controller
- ISA multi-I/O card if practical
- serial terminal as permanent fallback

The first system should not depend on a PC/AT keyboard controller.

## 13. Interrupts

Interrupt support is optional initially.

Early system operation may be polling-based.

Later CPLD interrupt logic may:

- collect ISA IRQ lines
- present pending interrupt bits to the VM
- provide simple priority encoding
- support at least floppy IRQ6 and optional VGA/other IRQs

A full 8259-compatible interrupt controller is not required unless deliberately chosen later.

## 14. DMA

DMA is explicitly deferred.

The first PDR-16/AT should not implement ISA DMA.

This means some ISA peripherals may be unusable initially, or must be operated in programmed I/O modes.

Possible later DMA support:

- floppy DMA2 emulation if required
- CPLD-assisted memory transfer engine
- limited channel-specific DMA rather than full PC/AT compatibility

## 15. Software Architecture

### 15.1 VM First

The PDR-16/AT architecture should be specified as a virtual machine independent of the ATmega implementation.

The ATmega firmware implements this VM.

A future FPGA or custom CPU may implement the same VM more directly.

### 15.2 Forth System

The native software environment is Forth-like or Forth-derived.

Likely features:

- data stack
- return stack
- threaded execution model
- block storage vocabulary
- assembler or metacompiler
- monitor/debugger
- device words for ISA I/O

Example low-level words may include:

```forth
IO@       ( port -- byte-or-word )
IO!       ( value port -- )
CIO@      ( port -- byte )
CIO!      ( byte port -- )
ISAM@     ( addr -- value )
ISAM!     ( value addr -- )
SECTOR@   ( buffer lba -- status )
SECTOR!   ( buffer lba -- status )
OPEN      ( name -- fileid status )
READ      ( buffer count fileid -- actual status )
WRITE     ( buffer count fileid -- actual status )
CLOSE     ( fileid -- status )
LOAD      ( filename -- status )
```

Traditional Forth block words such as `BLOCK`, `BUFFER`, `UPDATE`, `FLUSH`, and `THRU` may be optional compatibility features rather than the primary storage model.

Exact stack effects and byte/word semantics remain to be defined.

## 16. Development Milestones

### Milestone 0: Repository and documentation

- create `PDR-16_AT` project structure
- document VM assumptions
- document bus transaction model
- document Mega pin assignments
- document CPLD partitioning

### Milestone 1: Mega diagnostics

- direct port access tests
- serial monitor diagnostics
- LED heartbeat
- basic command shell

### Milestone 2: CPLD handshake

- Mega writes command/data/address to CPLD
- CPLD reports DONE/BUSY
- no ISA card required
- logic analyser verifies handshake

### Milestone 3: Fake ISA cycle

- CPLD generates ISA-style timing into test pins
- verify BALE, IOR#, IOW#, MEMR#, MEMW# timing
- verify transceiver control strategy

### Milestone 4: ISA I/O read/write

- connect to ISA slot/card
- perform basic I/O read/write cycles
- read VGA status register if possible

### Milestone 5: VGA proof of life

- initialise or access VGA text mode
- write characters to display
- achieve `PDR-16/AT` screen output

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

### Milestone 8: Native PDR-16/AT environment

- Forth prompt on VGA or serial
- FAT floppy storage usable
- basic editor/monitor
- self-hosting experiments

## 17. Deferred Features

The following are explicitly deferred:

- FPGA CPU implementation
- full 16-bit ISA support
- ISA DMA
- bus mastering
- PC BIOS compatibility
- PC/AT keyboard controller compatibility
- IDE hard disk support
- USB support
- advanced graphics modes
- multitasking
- full interrupt controller

## 18. Guiding Principle

The PDR-16/AT is not a PC clone.

It is a PDR/Forth-native 16-bit word machine that uses selected ISA/PC-AT cards as intelligent peripherals.

The architecture should remain simple, inspectable, and evolvable.

