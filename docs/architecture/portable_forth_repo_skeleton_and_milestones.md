# Portable Forth Repo Skeleton And Milestones

## 1. Intent

This note defines a concrete starting shape for the new portable Forth project.

The new repository is the portable core:

- it owns the generic native VM
- it owns seed-image loading and export
- it owns source replay and progress reporting
- it owns interactive execution after build
- it does not own target-specific primitive packages

`PDR-16_XT` remains a consumer of that core.

## 2. Repository Boundary

The new repo should not be a renamed copy of `PDR-16_XT`.

It should be a separate product with these responsibilities:

- portable VM runtime
- compiler/interpreter state
- dictionary and image management
- deterministic source replay
- build transcripts and diagnostics
- test harnesses for core behavior

`PDR-16_XT` keeps:

- its target primitive contract
- its seed-image generation rules
- its target libraries
- its hardware and simulator backends

## 3. Suggested Repository Name

Use a name that reads as a reusable core rather than a board project.

Suggested name:

- `portable-forth`

Alternative names if a narrower scope is preferred:

- `portable-forth-core`
- `forth-vm-core`
- `project-independent-forth`

## 4. Top-Level Layout

The first cut should be small and explicit.

```text
portable-forth/
  README.md
  LICENSE
  docs/
    architecture/
      portable_forth_repo_skeleton_and_milestones.md
      project_boundary.md
      primitive_contract.md
      seed_image_format.md
    logs/
      README.md
  core/
    vm/
    dictionary/
    compiler/
    parser/
    export/
  seed/
    builder/
    formats/
  adapters/
    console/
    filesystem/
    transcript/
  targets/
    xt/
      primitives/
      libraries/
      backend/
  tests/
    boot/
    replay/
    export/
    interactive/
  tools/
    scripts/
```

## 5. Package Responsibilities

### 5.1 `core/vm`

Holds the runtime state and execution loop.

Owns:

- instruction dispatch
- stack state
- interpreter/compiler mode transitions
- progress notifications

### 5.2 `core/dictionary`

Holds dictionary structures, linking, name lookup, and image growth.

Owns:

- headers
- names
- links
- XT resolution
- dictionary allocation

### 5.3 `core/compiler`

Holds source compilation behavior.

Owns:

- source line ingestion
- word compilation
- definition construction
- error reporting for source replay

### 5.4 `core/parser`

Holds text parsing helpers.

Owns:

- tokenization
- string handling
- source file ordering
- line-by-line replay support

### 5.5 `core/export`

Writes the expanded binary image.

Owns:

- deterministic serialization
- image metadata
- export validation
- checksum or manifest generation if needed

### 5.6 `seed/builder`

Prepares the initial boot image.

Owns:

- seed-image assembly rules
- boot-time constants
- compatibility with the portable VM loader

### 5.7 `adapters/*`

Provides host integration only.

Owns:

- file I/O
- console I/O
- transcripts
- terminal progress reporting
- environment-specific startup

### 5.8 `targets/xt`

Contains XT-specific consumers of the portable core.

Owns:

- XT primitive contract
- simulated XT primitives
- XT library sources
- XT-specific image rules

## 6. Minimal First-Cut Toolchain

The first implementation should be able to do only this:

1. load a seed image
2. initialize VM state
3. replay a fixed source order
4. compile the current library set
5. report progress and failures
6. export the grown image
7. re-enter an interactive prompt

That is enough to prove the repo is useful before the target adapters get large.

## 7. Milestone Plan

### Milestone 0: Repo skeleton

Goal:

- create the repository tree
- establish docs and ownership boundaries
- commit the initial empty structure

Exit criteria:

- repo can be cloned
- top-level layout is in place
- the role of each directory is documented

### Milestone 1: Seed image loader

Goal:

- load the existing seed image format into the portable core
- validate header and layout assumptions

Exit criteria:

- seed image boots in the core runtime
- loader errors are clear and deterministic

### Milestone 2: Dictionary and execution state

Goal:

- represent dictionary growth, name lookup, and execution state in the portable VM

Exit criteria:

- words can be defined and looked up
- interpreter and compiler state transitions are stable

### Milestone 3: Source replay loop

Goal:

- read a build-order file
- feed source text line by line
- compile in deterministic order

Exit criteria:

- current library order can be replayed
- compile progress is visible
- source errors identify the failing file and line

### Milestone 4: Deterministic export

Goal:

- write the expanded image back out
- keep output stable between runs

Exit criteria:

- exported images are reproducible
- image metadata or manifest matches the run

### Milestone 5: Interactive mode

Goal:

- continue into an interactive prompt after build completion

Exit criteria:

- words can be inspected and compiled interactively
- the runtime remains usable after source replay

### Milestone 6: XT target package

Goal:

- add the XT-specific primitive package as a consumer of the portable core

Exit criteria:

- XT libraries compile against the portable VM
- simulated primitives satisfy the current library contract

### Milestone 7: Reference validation

Goal:

- compare the portable path against the current simulator-based flow for spot checks

Exit criteria:

- the portable build and the reference build agree on the intended source set
- mismatches are explainable rather than accidental

## 8. First Implementation Slice

The best first code slice is:

- repository skeleton
- seed-image loader stub
- source-order replay stub
- progress callback interface
- transcript writer

That slice gives you a runnable spine without locking in target details too early.

## 9. Non-Goals For v1

Do not start with:

- cycle-accurate target emulation
- full board simulation
- hardware-specific peripheral behavior in the core
- a large generic Forth distribution
- target independence for every historical word

The first version should stay close to the current source corpus and the contract it actually needs.

## 10. Definition Of Done For The Repo Plan

This plan is good enough when:

- the repo boundary is explicit
- the core package list is fixed
- target ownership is clear
- the first milestone is achievable without hardware coupling
- the implementation order is obvious

