# 2026-05-12 Forth Commander Chat Transcript

## Summary

This chat defined `Forth Commander` as a commander-style browser for the PDR-16/XT Forth dictionary.

The initial idea included file browsing, but file I/O was explicitly set aside because it is not yet implemented. The focus moved to dictionary browsing only.

## Core Design Decisions

- Left pane is a hierarchical dictionary browser.
- Top level lists vocabularies.
- Entering a vocabulary lists populated bucket-table entries.
- Entering a bucket lists the words in that bucket, newest first.
- Each non-root level includes a `..` entry to go up one level.
- Vocabulary rows show populated bucket count.
- Bucket rows show word count.
- Word rows show `PRIM` for primitives or `:` for colon definitions.
- The breadcrumb field uses a separator like `->`, not `/`.
- The right pane remains independent so it can host later file browsing or other content.

## Colour And Visibility Rules

- ROM and RAM must be visually distinct.
- Colour families may be varied with the existing HSL ANSI library.
- Hidden helper words are still visible in the commander browser.
- Hidden helper words are invisible during normal `FIND` activity.
- Hidden helper words should use a slightly different colour shade.
- Hidden words are not the same thing as ROM/RAM.
- Selection always overrides normal row styling.

## PDR-16/XT Specific Clarifications

- This work is for the PDR-16/XT codebase, not V5.
- The current Forth image already provides useful kernel words such as:
  - `CONTEXT`
  - `CURRENT`
  - `VOCABULARY`
  - `DEFINITIONS`
  - `VOCAB>BUCKETS`
  - `>BUCKET`
  - `REWIND-VOCAB-BUCKETS`
  - `XT>NAME-IN-VOC`
  - `>NAME`
  - `NAME?`
  - `WORDS`
  - `SEE`
  - `FORGET`
- The current image also has `PRIVATE` and `REVEAL`, which are the right mechanism for hiding helper words inside the commander library.

## Documentation Added

The design was split into four architecture docs:

- `docs/architecture/forth_commander_spec.md`
- `docs/architecture/forth_commander_api.md`
- `docs/architecture/forth_commander_screen_contract.md`
- `docs/architecture/forth_commander_library_layout.md`

## Implementation Handoffs Added

The work was split into discrete implementation handoffs:

1. `docs/logs/2026-05-12_forth_commander_handoff_library_scaffold.md`
2. `docs/logs/2026-05-12_forth_commander_handoff_enumeration.md`
3. `docs/logs/2026-05-12_forth_commander_handoff_renderer.md`
4. `docs/logs/2026-05-12_forth_commander_handoff_actions.md`
5. `docs/logs/2026-05-12_forth_commander_handoff_index.md`

## Final Outcome

The spec work is complete.

The next chats can start implementation from the handoff files without re-deriving the architecture.

