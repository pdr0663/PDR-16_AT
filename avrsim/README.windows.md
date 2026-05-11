# Windows Build Notes

This repo can use a Windows-built `simavr` tree, so you do not need MSYS2 on
this machine if you build elsewhere and copy the binaries back.

Build it on the other Windows machine with MSYS2, using the `UCRT64` shell:

```sh
pacman -Syu
pacman -S --needed base-devel mingw-w64-ucrt-x86_64-toolchain mingw-w64-ucrt-x86_64-libelf
```

Add `mingw-w64-ucrt-x86_64-freeglut` only if you want the OpenGL example
programs too.

From the `simavr` checkout, build:

```sh
make all
```

What to copy back to this repo:

- the `simavr` executable from the build output
- `libsimavr.a`
- `libsimavrparts.a`
- any DLLs that `ldd` reports for the executable or examples you plan to run

If you want a self-contained folder, copy the executable next to its DLLs and
keep the directory together. If you only need the static libraries, copy those
into the matching `avrsim/simavr/...` build output on this machine or keep them
as a transfer bundle.

Known Windows-specific exclusions:

- `board_simduino` is skipped because the upstream notes still call out a
  file-mapping limitation on Win32.
- `board_usb` is skipped by default because it depends on optional VHCI USB
  support.

The source-side build logic lives in:

- `avrsim/simavr/Makefile.common`
- `avrsim/simavr/examples/Makefile`
- `avrsim/simavr/examples/Makefile.opengl`
