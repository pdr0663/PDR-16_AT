# VGA references

These are the best references found so far for bringing up and programming an ISA VGA card before the exact board chipset is known.

## Good starting references

- OSDev VGA Hardware
  - <https://wiki.osdev.org/VGA_Hardware>
  - Good practical overview of VGA blocks, ports, register groups, memory planes, and timing.

- IBM VGA/XGA Technical Reference Manual (draft)
  - <https://www.eserviceinfo.com/downloadsm/80788/IBM_IBM%20VGA%20XGA%20Technical%20Reference%20Manual%20May92.html>
  - Useful deeper reference for IBM VGA behavior, register model, and subsystem organization.

- Ardent Tool IBM technical-reference catalog
  - <https://www.ardent-tool.com/docs/catalog/pcdcat.html>
  - Useful index when chasing IBM adapter and system reference material.

## What these references are good for

- Standard VGA register access
- Text mode and planar graphics mode setup
- Port map expectations for VGA-compatible hardware
- Video memory organization
- CRT timing concepts for safe mode setting

## Important limitation

These are VGA-standard references, not exact board manuals for your specific card.

Exact board documentation usually depends on the VGA chipset, commonly something like Trident, Tseng Labs, Paradise/WD, Oak, Cirrus Logic, or an IBM adapter. Once you have the main chip marking, we can usually find a much more precise datasheet or programmer's reference.

## Next identification step

When you have a clear photo or a chip marking from the card, record it in:

- `C:\Users\pdr0663\PDR-16_XT\hardware\isa_cards\vga\README.md`

Then we can search for the exact chipset manual.

