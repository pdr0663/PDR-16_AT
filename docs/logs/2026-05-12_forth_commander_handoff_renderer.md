# Forth Commander Handoff - ANSI Screen Renderer and Colour Contract

## Scope

Implement the text-mode UI for `Forth Commander`.

This track is about screen layout and colour handling, not dictionary traversal internals.

## Current State

The screen contract is already written:

- [forth_commander_screen_contract.md](../architecture/forth_commander_screen_contract.md)

The ANSI library already exists and uses HSL-based colour helpers:

- `tools\forth\Forth Sources\04-ansi.fs`

The editor source shows the current text-mode style and key handling approach:

- `tools\forth\Forth Sources\08-editor.fs`

## Implementation Goal

Build the commander screen with:

- title row
- left pane dictionary browser
- right pane independent companion area
- bottom status/help row

The renderer should support:

- breadcrumb display
- level title display
- selection highlight
- ROM/RAM colour families
- hidden-helper dimming or alternate shade
- `PRIM` versus `:` labels

## Constraints

- Text mode first.
- ANSI-first implementation is preferred.
- Keep the layout usable in monochrome.
- The right pane must remain independent.
- Do not hard-wire file browsing yet.

## Suggested Files

- `tools\forth\Forth Sources\09-forth-commander.fs`
- reuse `04-ansi.fs` for colour helpers rather than inventing new ones

## Definition Of Done

- The commander UI draws a stable pane layout.
- The left pane shows the hierarchical browser data.
- The breadcrumb and level title are visible.
- Selection is obvious.
- ROM/RAM colours are distinct.
- Hidden helper words are slightly dimmer or otherwise distinguishable.

## Suggested Prompt For Next Chat

`Implement the ANSI text-mode renderer for Forth Commander. Use the existing HSL colour helpers, draw a commander-style two-pane layout, show breadcrumbs and level titles, and render selection, ROM/RAM, and hidden-helper states clearly.`

