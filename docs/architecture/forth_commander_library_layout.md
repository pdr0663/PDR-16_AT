# Forth Commander Library Layout

## 1. Purpose

This document is the last spec-side step before implementation.

It sketches how `Forth Commander` should be packaged as a Forth library inside its own vocabulary, using the existing `PRIVATE` and `REVEAL` mechanisms already present in the PDR-16/XT image.

## 2. Packaging Strategy

`Forth Commander` should be delivered as a normal source file in the Forth source tree, not as a special-case tool.

Recommended placement:

- `tools\forth\Forth Sources\09-forth-commander.fs`

The exact filename is not important, but the library should sit beside the other source-built components such as ANSI, math, and the editor.

## 3. Library Vocabulary

The library should define its own vocabulary and keep its implementation words inside that vocabulary.

Conceptual shape:

```forth
VOCABULARY FORTH-COMMANDER
FORTH-COMMANDER DEFINITIONS
```

Public entry points may remain visible.
Helper words should be private where appropriate.

## 4. Visibility Model

The current system already supports `PRIVATE` and `REVEAL`.

That is the right mechanism for this library:

- words marked `PRIVATE` are hidden from normal `FIND`
- hidden words are still part of the dictionary
- the commander browser may still show them
- the browser should show them in a slightly different colour

This matches the intended behaviour precisely:

- hidden during ordinary search activity
- visible as internal helpers inside the commander browser
- not confused with ordinary public application words

## 5. Proposed Library Entry Points

The public surface should be minimal.

Suggested entry points:

- `FCOMMANDER` or `FORTH-COMMANDER`
  - starts the browser
- `FCM-INIT`
  - prepares browser state
- `FCM-RUN`
  - runs the interactive loop

The exact names can still be adjusted, but the public surface should remain small.

## 6. Suggested Internal Word Families

The implementation will likely need helper words in these groups:

### 6.1 Browser State

- context creation
- selection movement
- breadcrumb construction
- level transitions

### 6.2 Enumeration

- vocabulary list enumeration
- bucket list enumeration
- word list enumeration
- populated-count calculation
- word-kind classification
- residency classification

### 6.3 Rendering

- pane drawing
- row drawing
- status line drawing
- colour selection
- selection highlighting

### 6.4 Actions

- open
- up
- `SEE`
- `FORGET`
- refresh

### 6.5 Internal Dictionary Access

- word-name lookup
- header-to-name conversion
- vocabulary-to-bucket-table conversion
- bucket traversal
- private-word detection

## 7. Private Helper Policy

Within the `FORTH-COMMANDER` vocabulary, helper words should default to private unless they are part of the intended public API.

This keeps the surface small and ensures the library behaves like a self-contained tool rather than a collection of unrelated support words.

Recommended rule:

- public words: the browser entry points only
- private words: everything else unless a reason exists to expose it

## 8. How The Browser Should Treat Private Words

Private words are not the same as ROM words or RAM words.

They are an orthogonal visibility class.

The commander browser should therefore present four states independently:

- ROM or RAM
- public or private
- primitive or colon
- selected or unselected

Suggested visual treatment:

- private helper word: same residency family, slightly dimmer or less saturated
- public word: normal residency family
- primitive word: explicit `PRIM`
- colon word: explicit `:`

## 9. Minimal Implementation Order

The first implementation should probably proceed in this order:

1. create the new vocabulary and public entry point
2. implement browser state records
3. implement vocabulary enumeration
4. implement bucket enumeration
5. implement word enumeration
6. add private-word colour treatment
7. wire up the text renderer
8. add `SEE` and `FORGET`

## 10. Intended Handoff Outcome

After this document, the spec work is complete.

The next chat can move directly into implementation with:

- a clear vocabulary boundary
- a known visibility model
- a screen contract
- a browser API contract
- a packaging target in the source tree

