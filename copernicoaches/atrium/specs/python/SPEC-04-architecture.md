# SPEC-04 — Architecture

## Layers

```
┌─────────────────────────────────────┐
│           Display (Textual)         │  renders state → no logic
├─────────────────────────────────────┤
│         Navigation / Controller     │  handles input → updates state
├─────────────────────────────────────┤
│              State Model            │  single source of truth
├─────────────────────────────────────┤
│          Filesystem Adapter         │  reads dirs/files → no UI knowledge
└─────────────────────────────────────┘
```

## Layer responsibilities

**State model**
- Holds: `current_dir`, `parent_dir`, `current_entries`, `selected`, `preview_target`
- No side effects; updated only by the controller

**Filesystem adapter**
- Lists directory contents
- Reads file metadata
- Handles permission errors
- Has no knowledge of navigation or display

**Navigation / Controller**
- Handles keyboard events
- Calls the filesystem adapter
- Mutates state
- Contains no rendering code

**Display (Textual)**
- Renders state into three columns
- Applies styles and highlights
- Minimum contract: `render(state)`
- Does not modify state or access filesystem

## Decoupling rules

- Display ← does not call filesystem or modify state
- Controller ← does not know rendering details
- Filesystem adapter ← does not know about navigation or display

## Extensibility

The architecture allows — without changing navigation or state:
- Swapping the display backend (e.g. Rich → Textual → other)
- Specialising the right column per file type
- Adding new input event types

## MVP constraints

- Single view (three columns)
- No plugin system
- No persistence beyond process lifetime

## Architectural rule

> The system must work correctly without the display layer.
> The display is a projection of state, not its driver.

## Stack

- Python 3.12+
- [Textual](https://textual.textualize.io/) for TUI rendering and keyboard event loop
