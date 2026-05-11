# avrsim Source Build Architecture

This note describes the intended simulator build split for `PDR-16/AT`.
The goal is to keep the runtime simulator separate from the source build
pipeline, the same way the old Python-based Forth build kept image generation
separate from the VM runtime.

## Core idea

`simavr` is a build-time dependency, not a permanent runtime dependency of this
repo.

The preferred workflow is:

1. build `simavr` on a Windows machine with MSYS2/UCRT64
2. copy the resulting binaries and DLLs into the `avrsim/` folder in this repo
3. run the simulator and Forth tooling from those copied artifacts

That keeps the source tree portable while avoiding a full Windows toolchain on
this machine.

## Artifact folder

Use the `avrsim/` folder itself as the artifact drop location.

That folder is ignored by git for binary outputs, so it can stay in the repo
without collecting build noise.

## What belongs there

Typical contents are:

- `avrsim.exe`
- `libsimavr.a`
- `libsimavrparts.a`
- any DLLs required by the executable or helper tools
- optional example binaries if you want them

The exact DLL set depends on what `ldd` reports on the build machine.

## Build-time vs runtime responsibilities

### Build machine

The build machine is responsible for:

- compiling `simavr`
- compiling the parts library
- gathering the runtime DLLs
- producing a clean artifact bundle

### This machine

This machine is responsible for:

- consuming the copied simulator binaries
- running the Forth system
- feeding Forth source files into the simulator
- processing post-compile binaries and manifests

## Relationship to the old Python build

The old PDR-16 system had a Python-led image build pipeline:

- Python was the source-of-truth builder
- generated ROM/image artifacts were checked into the runtime build path
- the VM consumed generated output rather than rebuilding itself at runtime

The same split should apply here:

- the simulator binary is an external build artifact
- the Forth system and capture tools consume that artifact
- the repo keeps the source of truth in scripts, manifests, and docs

## Source build path

The current build contract is:

- Windows build machine uses MSYS2/UCRT64
- simulator sources live in the build machine's own checkout
- build result is copied into `avrsim/`
- runtime scripts and docs refer to the copied binary, not to the build host

## What still needs tooling

The repo still needs a clean end-to-end source-fed simulation workflow for:

- launching the simulator from copied artifacts
- feeding Forth source files
- capturing the resulting transcript
- exporting or reconstructing the post-compile binary image

That work should build on the simulator artifact folder instead of hard-coding
WSL-only paths or Linux-specific temporary locations.

On Windows, the interactive terminal should be Tera Term, connected either to
the simulator's COM port or to a named pipe endpoint if the simulator exposes
one.
