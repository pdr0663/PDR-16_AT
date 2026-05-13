# Project Independent Forth System Specification

## 1. Purpose

This document defines the project-independent Forth system as a generic native VM plus target-specific primitive packages.

The VM is the portable engine used to build, run, and export Forth binaries.

The target project provides primitive words and libraries that are specific to that target. Those target assets may be backed by either simulation or real hardware.

## 2. Core Terms

### 2.1 Generic VM

The generic VM is the target-agnostic Forth runtime and compiler.

It must be able to:

- load a seed image
- execute the core Forth binary
- accept source input in deterministic order
- report compile progress and failures
- grow the dictionary
- export an expanded binary image
- run interactively after the build completes

The implementation language of the generic VM is not fixed by this spec.

### 2.2 Primitive Contract

The primitive contract is the set of low-level Forth words required by a target's libraries.

Libraries depend on the primitive contract, not on the implementation language or internal structure of the VM.

### 2.3 Target Primitive Backend

A target primitive backend provides the words required by that target's libraries.

Each target may have more than one backend:

- simulated backend for host-side development
- hardware backend for the actual machine

The same library source code must be usable against both backends where the target chooses to support that.

## 3. Project Boundary

The portable project owns the generic VM and its host-side tools.

The target project owns:

- the target primitive contract
- simulated primitive implementations
- hardware primitive implementations
- target-specific Forth libraries
- target-specific image format rules

This separation is required so target projects do not become the permanent root of the Forth toolchain.

## 4. Build Mode

The build system must be able to:

1. start the generic VM
2. load the core seed image
3. attach the appropriate target primitive backend
4. feed library source files to the VM
5. observe compilation progress
6. receive the expanded binary image

The build system must not require manual source replay through a simulator bridge unless that is the chosen backend for a target project.

## 5. Interactive Mode

After the binary is built, the same VM must be able to enter interactive mode.

Interactive mode is required so a user can:

- inspect words
- compile new definitions
- test features
- diagnose source or primitive issues

The interactive environment may expose target primitives from the simulated backend or the hardware backend, depending on the selected build profile.

## 6. Simulation Mode

A target project may provide a simulated backend that models target-specific primitives without real hardware.

Simulation mode is useful for:

- fast development
- source-level debugging
- regression testing
- library validation before hardware exists

Simulation mode is an implementation strategy for the target primitive package, not a requirement of the generic VM.

## 7. Hardware Mode

A target project may also provide a real hardware backend that implements the same primitive contract on the actual machine.

The hardware backend may be written in:

- C
- another C dialect
- another systems language
- assembly
- or any other implementation strategy that satisfies the contract

The implementation language is not part of the contract.

## 8. Library Policy

Each target owns its own Forth library set.

Libraries may be shared between targets only when their primitive requirements are compatible.

The spec does not assume that libraries are portable across targets by default.

## 9. Acceptance Criteria

The system is acceptable when:

- the generic VM boots from the seed image
- the target primitive backend satisfies the library contract
- the build process can feed source and observe progress
- the build process can export a deterministic binary image
- the resulting VM can run interactively
- simulation and hardware backends can be selected independently

## 10. Relationship to Other Projects

`PDR-16_XT` and future projects are consumers of the portable Forth system.

Each project may define:

- its own primitive words
- its own library set
- its own simulated backend
- its own hardware backend

The portable project remains responsible for the generic VM only.
