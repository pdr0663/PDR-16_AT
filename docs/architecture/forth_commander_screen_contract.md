# Forth Commander Screen Contract

## 1. Purpose

This document defines the screen-level contract for `Forth Commander`.

It sits between the browser API and any actual renderer, whether that renderer is ANSI text or direct VGA text mode.

## 2. Base Layout

The first implementation should assume an 80-column text display.

Recommended layout:

- top row: title
- left pane: dictionary browser
- right pane: independent companion pane
- bottom row: key hints or status

The panes should be visually separated with box drawing or clear ASCII borders.

## 3. Left Pane Contract

The left pane must show:

- a breadcrumb field
- the current level title
- a row list
- a visible selection marker

### 3.1 Breadcrumb Field

Example:

```text
FORTH -> A -> ABS
```

The breadcrumb should be a fixed header area near the top of the left pane.

### 3.2 Level Title

The level title should make the current mode obvious:

- `VOCABULARIES`
- `BUCKETS`
- `WORDS`

### 3.3 Selection Marker

The selected row should always stand out, even in monochrome.

Recommended options:

- reverse video
- bright foreground
- strong background contrast

## 4. Right Pane Contract

The right pane is independent from the left pane.

Its contents are not defined by the dictionary browser itself.

This allows the pane to be used later for:

- `SEE` output
- file browsing
- help text
- word metadata
- diagnostics

The left pane must not depend on the right pane for navigation state.

## 5. Row Styling

Each row can carry three visual attributes:

- selection state
- residency state
- kind state
- visibility state

### 5.1 Residency State

ROM and RAM should use different colour families.

Suggested families:

- ROM: blue / cyan / azure family
- RAM: green / yellow / lime family

The family should remain consistent down the tree:

- vocabulary determines the base family
- buckets inherit from vocabulary
- words inherit from bucket

### 5.2 Kind State

Word kind should still be obvious even when colour is used.

Recommended indicators:

- primitive: `PRIM`
- colon definition: `:`

### 5.3 Visibility State

Hidden helper words should still be shown in the commander browser, but with a slightly different shade.

They should not look like ordinary visible application words.

Suggested treatment:

- keep the same family as the parent vocabulary
- reduce brightness or saturation slightly
- preserve the explicit word name and kind label

These words are hidden only from normal `FIND` activity, not from the commander browser itself.

### 5.4 Selection State

Selection should override the normal row styling.

If a row is selected, selection style wins over residency style.

## 6. Monochrome Behaviour

The browser must still work if colour is disabled or unavailable.

In monochrome mode:

- selection remains obvious
- ROM/RAM distinction falls back to text labels or intensity
- `PRIM` and `:` remain visible as explicit text
- hidden helper words remain visible, but in a subtly different colour

## 7. Status Line

The bottom line should expose the active context and key bindings.

Recommended baseline hints:

- `ENTER=open`
- `ESC=up`
- `F3=SEE`
- `F8=FORGET`
- arrows=move

If the right pane is repurposed later, the status line should continue to describe only the current navigation semantics.

## 8. Colour Handling

The existing ANSI library uses HSL-based colour helpers.

That makes it practical to vary brightness or saturation within a base family while keeping ROM and RAM visually distinct.

Recommended use:

- base colour family for residency
- brighter variant for selection
- dimmer variant for breadcrumb or metadata

## 9. Text Mode First

The first implementation should be designed so it works in pure text mode.

Direct VGA rendering can later reuse the same pane, row, and colour semantics.
