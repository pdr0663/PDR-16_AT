# Forth Commander API Draft

## 1. Purpose

This document defines the browser-facing Forth API for `Forth Commander`.

The API is intentionally separated from screen drawing so the same navigation model can drive:

- the left dictionary pane
- future right-pane tools
- a later file browser

The first target is the dictionary browser described in `forth_commander_spec.md`.

## 2. Model

The browser exposes a hierarchical view with three levels:

1. vocabularies
2. buckets within a vocabulary
3. words within a bucket

Each browser pane should operate on an opaque browser context.

This keeps left- and right-pane state independent.

## 2.1 Existing Kernel Surface

The current image already exposes useful dictionary and naming support words that the browser can build on:

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

The browser API below is a presentation and navigation contract layered on top of that kernel surface.
The screen contract that consumes this API is defined in `forth_commander_screen_contract.md`.

The `Forth Commander` implementation itself should live in its own vocabulary, with helper words hidden where appropriate.

## 3. Opaque Context

A browser context is an opaque handle.

The implementation may store it as:

- an address
- a user variable pointer
- a heap object
- a small record in RAM

The API does not require the caller to know which representation is used.

### Required context properties

Every context must support:

- current level
- current selection index
- parent context, if any
- visible row count
- row metadata queries
- open/down navigation
- up navigation

## 4. Context Creation And Navigation

Suggested words:

```forth
FC-ROOT-CTX   ( -- ctx )
FC-UP         ( ctx -- ctx' )
FC-OPEN       ( ctx index -- ctx' )
FC-SELECT!    ( ctx index -- ctx )
FC-SELECT@    ( ctx -- index )
FC-LEVEL@     ( ctx -- u )
FC-PARENT@    ( ctx -- ctx' | 0 )
```

Interpretation:

- `FC-ROOT-CTX` creates or returns the top-level vocabulary browser context.
- `FC-UP` returns the parent context.
- `FC-OPEN` opens the currently selected row or a specific row index.
- `FC-SELECT!` changes the highlighted row without changing the current level.
- `FC-SELECT@` reports the highlighted row.
- `FC-LEVEL@` returns the current browser depth.
- `FC-PARENT@` returns the parent context or `0` at the root.

## 5. Row Enumeration

The browser should provide row-based enumeration for the current context.

Suggested words:

```forth
FC-ROWS      ( ctx -- u )
FC-ROW-NAME$ ( ctx index -- c-addr u )
FC-ROW-META  ( ctx index -- u )
FC-ROW-KIND  ( ctx index -- kind )
FC-ROW-ROM?  ( ctx index -- flag )
FC-ROW-RAM?  ( ctx index -- flag )
FC-ROW-OPEN? ( ctx index -- flag )
```

### Row kind

Suggested row kinds:

- `VOCAB`
- `BUCKET`
- `PRIM`
- `COLON`
- `HIDDEN`

### Row metadata

`FC-ROW-META` is the numeric value shown beside the row name.

By level, it means:

- vocabulary level: populated bucket count
- bucket level: word count
- word level: no extra count needed, so `FC-ROW-META` may be `0` or repurposed later

The display layer should not hard-code any other meaning into this field.

## 6. Vocabulary-Level Queries

Suggested words:

```forth
FC-VOCAB-COUNT       ( -- u )
FC-VOCAB-NAME$       ( i -- c-addr u )
FC-VOCAB-POPULATED#  ( i -- u )
FC-VOCAB-ROM?        ( i -- flag )
FC-VOCAB-RAM?        ( i -- flag )
```

Expected behaviour:

- vocabularies are listed at the root level
- the first implementation may use the active context search order as the vocabulary source
- if a broader registry is added later, the UI contract should not need to change
- only populated bucket-table entries contribute to `FC-VOCAB-POPULATED#`
- residency should be visible for colour selection

## 7. Bucket-Level Queries

Suggested words:

```forth
FC-BUCKET-COUNT     ( vocab -- u )
FC-BUCKET-NAME$     ( vocab bucket -- c-addr u )
FC-BUCKET-WORDS#    ( vocab bucket -- u )
FC-BUCKET-ROM?      ( vocab bucket -- flag )
FC-BUCKET-RAM?      ( vocab bucket -- flag )
FC-BUCKET-POPULATED? ( vocab bucket -- flag )
```

Expected behaviour:

- only non-vacant buckets are exposed to the browser
- the bucket count shown in the UI is the number of words in that bucket

## 8. Word-Level Queries

Suggested words:

```forth
FC-WORD-COUNT     ( vocab bucket -- u )
FC-WORD-NAME$     ( vocab bucket word -- c-addr u )
FC-WORD-XT        ( vocab bucket word -- xt )
FC-WORD-PRIM?     ( vocab bucket word -- flag )
FC-WORD-COLON?    ( vocab bucket word -- flag )
FC-WORD-SEE?      ( vocab bucket word -- flag )
FC-WORD-FORGET?   ( vocab bucket word -- flag )
FC-WORD-ROM?      ( vocab bucket word -- flag )
FC-WORD-RAM?      ( vocab bucket word -- flag )
```

Expected behaviour:

- words are listed newest first
- primitives are marked `PRIM`
- colon definitions are marked `:`
- hidden helper words are marked separately and remain viewable in the commander browser
- only colon definitions are viewable with `SEE`
- only RAM words are candidates for `FORGET`
- hidden helper words should not participate in normal `FIND` results

## 9. Breadcrumb Support

The browser should be able to build a breadcrumb string from the active context.

Suggested word:

```forth
FC-PATH$  ( ctx -- c-addr u )
```

Example:

```text
FORTH -> A -> ABS
```

The breadcrumb builder should use a separator that is not part of normal Forth names.

## 10. Enumeration Order

The API should preserve these rules:

- root vocabulary list: stable system order
- bucket list: non-vacant entries only
- word list: newest first

If the implementation later needs a different traversal for efficiency, the screen contract should stay the same.

## 11. Presentation Hints

The API should expose enough information for the renderer to colour rows by residency.

Recommended colour inputs:

- vocabulary residency
- inherited bucket residency
- inherited word residency
- current selection
- `PRIM` versus `:` distinction

The HSL ANSI library already supports colour-family variation, which makes this practical.

## 12. Minimal Implementation Target

The smallest useful first pass should support:

- root vocabulary listing
- one-level down into buckets
- one-level down into words
- `FC-PATH$`
- `FC-WORD-SEE?`
- `FC-WORD-FORGET?`
- hidden helper visibility

That is enough to build the browser shell without committing to file I/O or other right-pane features.

The practical backing for that first pass can come from:

- `CONTEXT @`
- `FIND-VOCS`
- `WORDS`
- `XT>NAME-IN-VOC`
- `>NAME`
- `SEE`
- `FORGET`

Hidden helper words in the `Forth Commander` vocabulary should not be exposed through normal search, but the browser must still be able to show them with a distinct colour.
