## Floppy disk controller card

### Provenance

- Source listing: <https://www.ebay.com.au/itm/327089507326>
- eBay item number: `327089507326`
- Listing title seen during research: `Vintage Western Digital WD37C65BJM 8-Bit ISA Floppy Disk Controller Card - 1987`

### Identification status

Current best identification from the listing is:

- main controller family: `Western Digital WD37C65`
- package/variant named in listing: `WD37C65BJM`
- bus form factor: `8-bit ISA`

This is much stronger identification than we have for the VGA card, but it is still worth confirming against the physical board markings when the card is in hand.

### Likely significance

The WD37C65 family is more integrated than a bare `uPD765`-style controller. It typically combines floppy controller logic with subsystem support features used in PC-compatible designs.

That means the `uPD765` command model is still relevant, but the `WD37C65` family datasheet is the more important board-level reference.

### What to capture from the physical card

- Clear front and back photos
- Exact chip markings
- Connector types present
- Jumper or DIP switch positions
- Any BIOS ROM fitted, with part number
- PCB model number or silkscreen identifier

### Related docs

- `C:\Users\pdr0663\PDR-16_AT\docs\peripherals\isa_cards\floppy_disk_controller\references.md`

