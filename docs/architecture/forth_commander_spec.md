# Forth Commander Specification

## 1. Purpose

`Forth Commander` is a text-mode interactive browser for the PDR-16/XT Forth dictionary.

The immediate goal is to provide a commander-style navigation interface for:

- vocabularies
- bucket-table entries within a vocabulary
- words within a bucket

File browsing is intentionally out of scope for the first version.

The Forth-facing enumeration contract is defined in `forth_commander_api.md`.
The pane layout and colour contract are defined in `forth_commander_screen_contract.md`.
The source packaging and vocabulary boundary are defined in `forth_commander_library_layout.md`.

`Forth Commander` itself should be implemented as a Forth library inside its own vocabulary.
Helper words may be hidden where appropriate.

## 2. Design Goals

The interface should:

- feel like a dual-pane commander utility
- make dictionary exploration fast and visual
- distinguish ROM and RAM words clearly
- make viewable and non-viewable words obvious
- stay usable in monochrome if colour is unavailable
- leave the right pane independent so other tools can co-exist later

## 3. Left Pane: Hierarchical Dictionary Browser

The left pane is a three-level tree:

1. vocabulary list
2. bucket list for the selected vocabulary
3. word list for the selected bucket

Each non-root level begins with a `..` entry that returns to the previous level.

### 3.1 Vocabulary Level

At the top level, each row represents a vocabulary.

Each vocabulary row should show:

- vocabulary name
- number of populated bucket-table entries

Example:

```text
FORTH           [17]
ASSEMBLER       [12]
EDITOR           [8]
```

### 3.2 Bucket Level

When a vocabulary is entered, the next level lists only non-vacant bucket-table items.

Each bucket row should show:

- bucket identifier or label
- number of words in that bucket

Example:

```text
..
A                [4]
C                [7]
D                [2]
```

### 3.3 Word Level

When a bucket is entered, the next level lists the words in that bucket.

Words should be listed newest first.

Each word row should show:

- word name
- `PRIM` for primitives
- `:` for colon definitions
- hidden helper words may be marked separately from both of those

Example:

```text
..
WORD3           [:]
WORD2        [PRIM]
WORD1           [:]
```

Primitive words are not viewable with `SEE`.
Colon words are viewable with `SEE`.
Hidden helper words are still viewable, but they are not visible during normal `FIND` activity.

## 4. Breadcrumb Field

The left pane should include a breadcrumb field showing the current location in the dictionary tree.

Example:

```text
FORTH -> A -> ABS
```

The separator should not rely on `/`, since `/` may be undesirable in future word naming or file-related contexts.

## 5. Right Pane

The right pane is intentionally independent from the left pane.

Its initial contents are not fixed by this specification.

This keeps room for later co-existence with:

- file browsing
- word information
- `SEE` output
- help text
- status summaries

The important rule is that left-pane navigation must not depend on the right pane.

## 6. Keyboard Behaviour

The interface should be keyboard driven.

Recommended baseline actions:

- `ENTER`: open the selected row
- `ESC`: go up one level or return to the previous context
- `F3`: view the selected word with `SEE` when the selected item is a colon definition
- `F8`: forget the selected word when it is in RAM and safe to remove
- arrow keys: move the selection

## 7. ROM and RAM Visibility

ROM and RAM are essential distinctions and should be visible in the UI.

Suggested policy:

- vocabularies in ROM and RAM use different colour families
- buckets inherit the colour family of their parent vocabulary
- words inherit the colour family of their parent bucket
- selection still uses reverse video or a strong highlight, regardless of residency
- hidden helper words should use a slightly different shade so they remain visually distinct

This means colour communicates both structure and residency.

The HSL-based ANSI colour library is a good fit because it allows base colours to be varied while preserving a consistent family.

## 8. Colour Policy

Colour should improve clarity, not replace textual meaning.

Use colour for:

- current selection
- ROM versus RAM residency
- breadcrumb emphasis
- `PRIM` versus `:` distinction, if helpful
- hidden helper word visibility

Even when colour is enabled, the text labels should still remain explicit.

## 9. Ordering Rules

Ordering rules should be stable and simple:

- vocabularies: system-defined or discovery-defined order, to be finalized later
- buckets: only populated buckets are shown
- words: newest first

The word ordering choice matters because this is a working browser, not an archival listing.

## 10. Implementation Staging

The recommended implementation order is:

1. text-mode layout and navigation
2. vocabulary enumeration
3. bucket enumeration
4. word enumeration
5. `SEE` integration for colon definitions
6. `FORGET` integration for RAM words
7. colour refinement

This keeps the first version focused on the dictionary browser itself.

## 11. Exclusions For Now

The first version does not need:

- floppy file browsing
- FAT support
- block browsing
- editor integration
- command shell features

Those can be added later without changing the left-pane dictionary tree model.
