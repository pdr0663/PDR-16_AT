# Project Independent Forth System White Paper

## Abstract

This paper proposes a separate Project Independent Forth System with a generic native VM and a target-neutral primitive contract. `PDR-16_XT` becomes one consumer of that system rather than the project that defines it.

The generic VM is the portable development engine. It loads a core Forth binary, executes source files in order, reports compilation progress, grows the dictionary, and exports an expanded Forth binary. It does not know target details.

Target-specific behavior lives in primitive packages. A target project may provide a simulated primitive backend for host-side development and a real primitive backend for the actual machine. The same Forth library sources are compiled in both cases, but the available primitive words and resulting binaries are target-specific.

The intent is not to replace Forth with a host-language build system. The intent is to make the Forth runtime/compiler available as a reusable development engine across future projects, while keeping target variation in the primitive layer and target libraries.

## 1. Problem Statement

The current `PDR-16_XT` library compilation workflow is functionally correct but operationally slow. It uses a target-machine simulation loop to feed Forth sources line by line into the VM, waiting for compile completion between lines. That makes the simulator itself the bottleneck.

That workflow also couples three concerns that should be separated:

- seed-image generation
- Forth runtime execution and compilation
- target-specific primitive implementation or hardware simulation

For future Forth work, the core question is not how to make the simulator faster. The core question is how to make the Forth system itself available as a native host-side development engine with a clean primitive contract.

## 2. Design Position

The proposed architecture is:

- keep the seed Forth image generation in Python
- implement a generic native VM that consumes that seed image
- feed Forth source files directly to the VM
- expose compilation progress from the VM to the build harness
- export the resulting expanded Forth image as a binary artifact
- provide target-specific primitive backends outside the generic VM
- retain simulator-based replay only as a reference path, not the primary build path

This makes the Forth binary the stable, portable artifact, and makes `PDR-16_XT` one deployment target of that artifact rather than the definition of the whole system.

## 3. Goals

The portable native Forth VM should:

- boot from the existing seed image
- execute Forth source files in the same order used today
- compile and extend the dictionary in memory
- preserve the source-language semantics needed by the library set
- export a deterministic binary image after compilation
- run fast enough to make library development practical on the host
- remain independent of target hardware assumptions unless explicitly required by the seed image format

## 4. Non-Goals

The first version should not try to:

- emulate AVR instructions cycle-accurately
- reproduce the full hardware board design
- replace the Python seed-image builder
- implement every historical Forth feature ever used by the wider project family
- prove equivalence against the simulator before anything useful can ship

The generic VM should be scoped to the source patterns and dictionary operations actually needed by the current library set.

## 5. Architectural Separation

The proposed split has four layers.

### 5.1 Seed Image Layer

Python remains responsible for generating the initial binary image. That image is the bootable foundation for the portable VM.

This layer should remain machine-agnostic where possible, because the point of the seed is to provide a portable starting state rather than tie the system to one board.

### 5.2 Portable Forth Core

This is the new portable project.

It should contain:

- VM state
- dictionary storage
- word lookup and linking
- interpretation and compilation state
- source parsing
- export of the grown image

This layer is the reusable asset.

### 5.3 Target Primitive Packages

Target projects own primitive words that are not part of the generic VM.

Each target project may provide:

- a simulated primitive backend for host-side development
- a hardware primitive backend for the actual target system
- target-specific extension words used by that project's libraries

The library source set is shared across those backends where compatible.

### 5.4 Platform Adapters

Platform-specific concerns should sit outside the portable core:

- console I/O
- file loading
- image export location
- optional test harnesses
- any future target-specific hooks

The platform layer should not own the semantics of the Forth system.

## 6. Generic VM Contract

The generic VM must:

- load a seed image
- execute the booted Forth system
- ingest source files in a deterministic order
- report progress and errors to the build harness
- support interactive execution after build completion
- export a final binary image

The generic VM must not require knowledge of any one target's hardware layout, peripheral set, or primitive implementation details.

## 7. Project Boundary

This work should be treated as a separate portable Forth project, with `PDR-16_XT` as one client.

That means:

- the portable core owns the generic Forth engine
- `PDR-16_XT` owns its seed image, target primitive packages, source library set, and target-specific integration
- future projects can reuse the same core with different seed images or different image layouts

This boundary is useful because it prevents the XT checkout from becoming the permanent root of the Forth toolchain.

## 8. Source Handling Model

The current library flow is already source-driven. The portable VM should preserve that model.

The build sequence should look like this:

1. load the seed image
2. initialize the native VM
3. read the project build order
4. feed each source file into the VM
5. compile and link definitions into the dictionary
6. export the final image

The build harness must also be able to observe compilation progress and receive status from the VM while source is being compiled.

That preserves the source-order dependence of the current workflow while removing the simulator bottleneck.

The same VM must also support interactive execution after the image is built, so that a user can develop and test new features at the Forth prompt.

## 9. Verification Strategy

Long-term, the native core should be validated against the existing target-side workflow. However, early progress should not be blocked on full simulator equivalence.

The initial acceptance criteria should be internal and practical:

- the VM boots successfully from the seed image
- source files can be loaded and compiled
- the dictionary grows without corruption
- exported images are deterministic
- failures report enough context to debug source problems
- the same VM can run interactively after the build completes

Later, once the native path is useful, the simulator path can be used as a reference for spot checks and regression analysis.

## 10. Risks

### 10.1 Semantic Drift

A host-side VM can accept sources that the target-side runtime would reject, or it can build a slightly different dictionary layout.

Mitigation:

- keep the source subset narrow at first
- preserve the source language rules that matter for the current libraries
- add targeted checks around dictionary structure and word creation

### 10.2 Over-Emulation

It is easy to drift from portable Forth core into full target emulator.

Mitigation:

- keep the portable core focused on Forth semantics
- isolate hardware assumptions behind adapters
- refuse unnecessary target coupling unless a feature truly requires it

### 10.3 Scope Inflation

The project can grow into a general Forth distribution effort if the boundary is not explicit.

Mitigation:

- define the portable core as the product
- define `PDR-16_XT` as one consumer
- keep board-specific behavior out of the core

## 11. Recommended First Milestone

The first useful milestone should be:

- a native VM that loads the existing seed image
- a source feeder that replays the current library list
- progress reporting from the VM to the build harness
- a deterministic expanded image written back to disk
- a text transcript of the compile session
- an interactive prompt mode after the build

At that point, the system is already useful as a portable Forth development engine, even before deeper validation work is complete.

## 12. Recommended Project Split

### Remain In `PDR-16_XT`

- seed-image generation in Python
- source libraries
- target primitive packages
- image format used by XT
- target-specific documentation and integration

### Move To The Portable Forth Project

- generic VM core
- source parser and compiler runtime
- dictionary engine
- image export and persistence
- host-side test harnesses
- progress reporting and interactive console plumbing

## 13. Conclusion

The current simulator-based compilation path proved that the source set is viable, but it also exposed the wrong bottleneck: the target runtime is being used as the compiler.

The better design is to move the compiler/runtime into a portable native system with a generic VM contract. That preserves the Forth model, removes the simulator from the critical path, and turns the resulting binary into a reusable artifact for future Forth-based projects.

`PDR-16_XT` can then remain what it should be: one target and one source suite for a broader Forth development platform.
