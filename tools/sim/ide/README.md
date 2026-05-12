# Arduino IDE layouts

This tree keeps version-specific Arduino IDE support separate.

- `new/`
  - Arduino IDE 2.x and `arduino-cli`-based support files
- `old/`
  - Arduino IDE 1.8.x and legacy toolchain support files

Keep machine-specific paths and resolver wrappers in the matching subtree so
different installs do not overwrite each other.
