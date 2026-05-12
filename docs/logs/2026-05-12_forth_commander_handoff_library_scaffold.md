# Forth Commander Handoff - Library Scaffold and Vocabulary Boundary

## Scope

Create the `Forth Commander` source module as a normal Forth library inside its own vocabulary.

This track is about packaging and module boundaries, not the browser logic itself.

## Current State

The design docs already define the intended structure:

- [forth_commander_spec.md](../architecture/forth_commander_spec.md)
- [forth_commander_api.md](../architecture/forth_commander_api.md)
- [forth_commander_screen_contract.md](../architecture/forth_commander_screen_contract.md)
- [forth_commander_library_layout.md](../architecture/forth_commander_library_layout.md)

The current Forth image already supports:

- `VOCABULARY`
- `DEFINITIONS`
- `PRIVATE`
- `REVEAL`

So the library can follow the same source-built style as the other modules.

## Implementation Goal

Add a new source file for the commander library and establish the public entry points plus hidden helper vocabulary.

Recommended public surface:

- `FCOMMANDER`
- `FCM-INIT`
- `FCM-RUN`

Recommended internal policy:

- keep helper words `PRIVATE` unless they are intended to be public
- keep all commander words inside the commander vocabulary
- do not leak implementation helpers into the global search space

## Suggested Files

- `tools\forth\Forth Sources\09-forth-commander.fs`

If the repo prefers a different numbering or inclusion point, keep the file adjacent to the other source-built libraries and update the build order accordingly.

## Constraints

- Do not introduce file I/O.
- Do not implement the renderer in this track.
- Do not add navigation semantics beyond the top-level entry points.
- Keep the module self-contained.

## Definition Of Done

- The commander source file exists.
- The library can be loaded as a normal Forth vocabulary/library.
- Public entry points are present.
- Helper words are hidden where appropriate.
- The source fits the repo’s existing library style.

## Suggested Prompt For Next Chat

`Implement the Forth Commander library scaffold as a new source file in the Forth source tree. Create the vocabulary boundary, public entry words, and private helper structure, but do not implement the browser logic yet. Keep the module self-contained and aligned with the existing PRIVATE/REVEAL pattern.`

