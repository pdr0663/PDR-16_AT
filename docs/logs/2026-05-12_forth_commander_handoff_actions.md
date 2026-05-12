# Forth Commander Handoff - Actions, Navigation, and Visibility Rules

## Scope

Implement the interactive behaviour of the commander browser.

This track is about what happens when the user moves, opens rows, views words, forgets words, or navigates up and down levels.

## Current State

The desired behaviour is already defined in the spec docs:

- [forth_commander_spec.md](../architecture/forth_commander_spec.md)
- [forth_commander_api.md](../architecture/forth_commander_api.md)

The current source image already has the underlying search and visibility tools:

- `SEE`
- `FORGET`
- `PRIVATE`
- `REVEAL`

## Implementation Goal

Implement the event loop and action logic for the commander browser:

- arrow-key movement
- `ENTER` to open the selected row
- `ESC` or `..` to go up a level
- `F3` to view a colon definition with `SEE`
- `F8` to `FORGET` a RAM word when allowed
- refresh/redraw after each state change

## Rules To Preserve

- Vocabulary level lists vocabularies.
- Bucket level lists only populated buckets.
- Word level lists newest first.
- `PRIM` words are not viewable with `SEE`.
- colon definitions are viewable with `SEE`.
- hidden helper words are still visible in the commander browser.
- hidden helper words remain hidden from normal `FIND`.
- ROM/RAM state should affect colour.
- selection should override normal row styling.

## Suggested Files

- `tools\forth\Forth Sources\09-forth-commander.fs`

## Definition Of Done

- A user can move through the three levels without leaving the browser.
- `SEE` works only when appropriate.
- `FORGET` is guarded so it only applies where safe.
- Hidden helper words show up with their distinct colour treatment.
- The right pane can remain idle or host later content without breaking navigation.

## Suggested Prompt For Next Chat

`Implement the commander browser interaction loop and action handling. Wire up movement, open/up navigation, SEE, and FORGET with the correct visibility and residency checks. Preserve newest-first ordering and the hidden-helper colour rule.`

