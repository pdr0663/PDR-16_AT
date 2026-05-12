# Forth Commander Handoff - Dictionary Enumeration and Browser API

## Scope

Implement the data-side browser layer that exposes vocabularies, buckets, and words to the commander UI.

This track is about enumeration and metadata, not drawing.

## Current State

The design and API contracts are already defined:

- [forth_commander_spec.md](../architecture/forth_commander_spec.md)
- [forth_commander_api.md](../architecture/forth_commander_api.md)

The current kernel already exposes useful words for this work:

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

The current system also has the private/public visibility mechanism needed for helper words.

## Implementation Goal

Build the browser-facing query layer that answers:

- how many vocabularies exist
- which bucket entries are populated
- how many words are in a bucket
- whether a word is primitive, colon, ROM, RAM, public, or hidden
- what breadcrumb path represents the current location

## Suggested API Targets

The next chat can choose final names, but the contract should cover these ideas:

- root browser context
- up/down navigation state
- row count and row metadata
- vocabulary count and populated-bucket counts
- bucket counts
- word kind and visibility
- breadcrumb string

## Constraints

- Preserve newest-first ordering for word listings.
- Keep vocab/bucket/word levels separate.
- Treat hidden helper words as visible to the commander browser, but invisible to normal `FIND`.
- Keep ROM/RAM classification available for colour and status decisions.

## Suggested Files

- `tools\forth\Forth Sources\09-forth-commander.fs`
- any small helper file if the implementation needs a clearer split, but keep the public surface in one place if possible

## Definition Of Done

- The browser layer can enumerate all three levels.
- The browser layer can report counts and names.
- The browser layer can distinguish `PRIM`, `:`, hidden helper words, and residency.
- The browser layer can produce breadcrumb text.

## Suggested Prompt For Next Chat

`Implement the commander dictionary enumeration layer on top of the existing kernel words. Provide vocabulary, bucket, and word queries; breadcrumb text; word kind and visibility flags; and the metadata needed by the UI. Keep newest-first ordering and preserve the hidden-helper visibility model.`

