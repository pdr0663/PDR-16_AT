# Segmented memory strategy

## Core model

The Forth-visible machine should present:

- `64K` words per segment
- word-oriented addressing by default
- a segment register used to select other `64K` word segments

The VM implementation on the Mega is responsible for translating this virtual model onto:

- Mega flash
- Mega SRAM
- ISA RAM
- ISA device memory
- ISA I/O space

The VM code itself, written as an Arduino sketch in C/C++, is **not** part of the Forth-visible address space.

## Segment 0 policy

Segment `0` is the primary Forth system segment.

The intended layout is:

- low part of segment `0`: ROM-like Forth image
- high part of segment `0`: as much writable RAM as can reasonably be mapped there

This gives a familiar and practical arrangement:

- kernel and precompiled dictionary low
- live writable workspace high

## Why this makes sense

`64K` words is a large space in Forth terms.

For the initial system, segment `0` should be able to hold nearly all of the normal Forth working environment if it is organized carefully:

- resident kernel
- core dictionary
- user area
- stacks
- TIB
- scratch buffers
- small local writable structures

The much larger user dictionary and bulk storage can then live in external ISA RAM segments.

## Draft shape of segment 0

This is intentionally conceptual rather than final:

- bottom region:
  - flash-backed ROM-like image
  - kernel code
  - precompiled words
  - cold-start structures
- top region:
  - SRAM-backed writable window
  - data stack
  - return stack
  - TIB
  - user variables
  - small buffers

The middle can remain either:

- unused for now
- reserved for future expansion
- partially mapped to other storage if needed

## Important implementation detail

The ROM-like part of segment `0` is a **VM mapping**, not a claim that the Mega exposes one flat readable word array in the same way as RAM.

In practice:

- flash-backed reads will use explicit VM helper logic
- SRAM-backed reads/writes will use normal RAM access
- the VM decides which backend to use from the segment and word address

## Suggested access policy by region

- local ROM-like region:
  - word reads allowed
  - writes either forbidden or handled only by special update tools
- local SRAM region:
  - normal word and byte access
- ISA RAM region:
  - normal word abstraction at the Forth level
  - physical byte or word cycles hidden by the memory manager
- memory-mapped device region:
  - byte-oriented or device-specific access policy
- I/O space:
  - separate from normal memory access

## Consequence for Forth semantics

This supports a clean programmer-facing model:

- `@` and `!` are normally word operations
- `C@` and `C!` are available for byte-sensitive cases
- ordinary RAM, even when physically on an `8-bit` ISA path, still appears as word memory
- device memory can be treated specially where needed

## Role of external ISA RAM

External ISA RAM is the natural home for:

- user dictionary growth
- larger data structures
- bulk buffers
- later file/block-related workspace

This avoids overcommitting the Mega's limited `8 KB` SRAM.

## Design intent summary

The current intended arrangement is:

- segment `0` contains the core Forth environment
- low addresses in segment `0` map to ROM-like flash-backed content
- high addresses in segment `0` map to scarce but valuable writable RAM
- other segments are selected through the segment register
- the VM implementation itself lives outside the Forth-visible memory map

## Concrete first-pass segment 0 layout

The most useful near-term model is:

- `segment 0` is the **entire normal Forth dictionary and execution space**
- all traditional near addresses are `16-bit` word addresses within segment `0`
- the VM hides the fact that segment `0` is physically backed by mixed storage

This preserves ordinary Forth assumptions for:

- links
- name headers
- code fields
- execution tokens
- compiled references
- `@` / `!` / `,` / `EXECUTE`

### Draft segment 0 map

This is a first-pass conceptual map, not yet a frozen numeric contract.

- low region:
  - flash-backed ROM-like kernel and precompiled dictionary
- middle region:
  - ISA RAM-backed user dictionary growth area
- high region:
  - Mega SRAM-backed writable local working set

### Example proportions

One plausible first cut is:

- about `32 KW` low ROM-like system space
- about `28 KW` ISA RAM-backed dictionary expansion
- about `4 KW` high local writable RAM window

That fills one logical `64 KW` segment:

- `0x0000 .. 0x7FFF` words:
  - ROM-like system image
- `0x8000 .. 0xEFFF` words:
  - ISA RAM-backed dictionary and bulk writable near-space
- `0xF000 .. 0xFFFF` words:
  - Mega SRAM-backed local writable space

The exact cut points can move, but the structural idea is the important part.

## What belongs in the high local RAM window

The top local writable window should hold the things that most benefit from being local and fast:

- data stack
- return stack
- user variables
- TIB
- scratch buffers
- interpreter/compiler transient state
- possibly a small block of local dictionary workspace if helpful

This avoids wasting scarce local SRAM on large dictionary growth.

## What belongs in the ISA-backed near region

The ISA-backed middle region is the natural place for:

- user dictionary growth
- colon definitions added after cold start
- variable storage that does not need to be especially local
- larger tables and buffers that still need to look like ordinary near memory

This is the key design move:

- the dictionary still appears to live in ordinary near memory
- the VM silently services those addresses from ISA RAM when they fall in the mapped range

## Why this solves the XT/link problem

Because the whole active dictionary remains in `segment 0`:

- links stay simple `16-bit` near addresses
- XTs remain simple near addresses
- compiled references remain simple near addresses

No segment word is needed in ordinary dictionary headers.

## Memory access model outside segment 0

Anything outside `segment 0` should be treated as **far data space**, not ordinary near dictionary space.

That means a reference outside segment `0` should conceptually be:

- `segment`
- `word offset`

rather than a plain near pointer.

## Recommended policy for non-zero segments

- `segment 0`:
  - normal Forth code and dictionary space
- non-zero segments:
  - far data
  - bulk buffers
  - optional RAM disks or block caches
  - device memory windows
  - later application-private spaces

I would avoid placing ordinary executable dictionary code in non-zero segments in the first version.

## Suggested far-access model

Use explicit far-memory words rather than making all normal Forth pointers segmented.

For example, conceptually:

- far fetch:
  - `( seg addr -- x )`
- far store:
  - `( x seg addr -- )`
- far byte fetch/store:
  - byte-oriented equivalents

The exact naming can be decided later, but the idea is:

- ordinary `@` / `!` remain near operations in `segment 0`
- explicit far words access other segments

This keeps most of the system traditional and easy to reason about.

## Suggested region types for non-zero segments

Not every non-zero segment has to obey the same policy.

A segment can be tagged by the VM as one of:

- far word RAM
- far byte RAM
- device memory
- reserved/unmapped

Then the memory manager can apply the correct low-level behavior:

- word RAM:
  - word-oriented abstraction
- byte RAM:
  - byte-oriented handling where needed
- device memory:
  - device-safe or region-specific access policy

## VGA and other device windows

Memory-mapped device windows, such as VGA memory, should generally **not** be treated as ordinary near dictionary memory.

They fit better as:

- dedicated non-zero segments
- or special mapped windows with explicit byte/device semantics

That avoids contaminating the main Forth dictionary space with device-specific access rules.

## Practical summary

The most workable first model is:

- `segment 0` is the stitched, conventional Forth near space
- its low part is ROM-like flash-backed
- its middle part is ISA RAM-backed
- its high part is local SRAM-backed
- all normal dictionary links and XTs remain near addresses
- everything outside segment `0` is explicit far space

That gives you a traditional Forth core with a segmented expansion model that stays under control.
