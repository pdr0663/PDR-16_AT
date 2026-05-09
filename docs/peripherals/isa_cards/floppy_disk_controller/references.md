# Floppy disk controller references

These references are useful for both generic PC/AT-compatible FDC work and the specific controller family identified from your eBay listing.

## Current board identification

From the eBay listing for item `327089507326`, the card is currently identified as:

- `Western Digital WD37C65BJM`
- `8-bit ISA`
- listing title: `Vintage Western Digital WD37C65BJM 8-Bit ISA Floppy Disk Controller Card - 1987`

Listing reference:

- <https://www.ebay.com/itm/327089507326>

## Chip-level references

- WD37C65B datasheet
  - <https://www.alldatasheet.com/datasheet-pdf/pdf/128748/NEC/WD37C65B.html>
  - Best match found for the controller family named in the listing. This is the most relevant starting reference for your actual card.

- NEC uPD765A / uPD765B datasheet
  - <https://www.alldatasheet.com/datasheet-pdf/pdf/129527/NEC/UPD765A.html>
  - Classic floppy controller reference. Useful because many later controllers preserve the same command model and host-visible behavior.

- Intel 82077AA datasheet
  - <https://www.alldatasheet.com/datasheet-pdf/pdf/167793/INTEL/82077AA.html>
  - Later single-chip PC-AT/PS-2-compatible controller with FIFO and strong compatibility notes. Good comparison reference for PC-compatible behavior.

- OSDev Floppy Disk Controller
  - <https://wiki.osdev.org/Floppy_Disk_Controller>
  - Practical programming reference with register map, command flow, and notes on standard PC-compatible behavior.

## Why the WD37C65 reference matters

The WD37C65 family is not just a bare formatter/controller. It is a floppy disk subsystem controller intended for PC-compatible designs, so it is the best match for understanding board integration details, drive interface behavior, and timing expectations beyond the classic `uPD765` command set.

## Common PC/AT defaults

The following are common PC/AT-compatible defaults for an ISA floppy controller card:

- Base I/O: `0x3F0` to `0x3F7`
- IRQ: `6`
- DMA: `2`

These values are typical rather than guaranteed. Verify them against the physical card, any jumper block, and the actual controller markings.

## What to capture from the card

- Main controller chip marking
- Any companion data-separator or bus-interface chips
- BIOS ROM presence and part number, if fitted
- Jumper or switch settings
- Connector set present on the bracket or PCB
- Any silk-screened model number

Once the card is identified, we can add model-specific docs here.
