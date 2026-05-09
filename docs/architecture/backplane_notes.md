# Backplane notes

## Current identified backplane

- `Advantech PCA-6108 Rev.A0`

## Current role in PDR-16/AT

This is the current ISA backplane platform for the machine.

It should be treated as a concrete hardware constraint rather than a generic PC/AT backplane, because details such as slot arrangement, connector style, grounding, and any passive routing choices may affect integration work.

## Questions this helps answer later

- How many ISA cards can be installed during development?
- Which slots are mechanically best for VGA and floppy?
- How should the custom daughterboard mate to the backplane?
- Are there any nonstandard power-entry or slot-grouping details?
- What real loading and stub lengths will the ISA control and data lines see?

## Next information to gather

- Photos of the backplane
- Any available manual or product sheet
- Slot count and type summary
- Power-input details
- Measurements useful for daughterboard placement
