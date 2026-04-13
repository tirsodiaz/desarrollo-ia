# SPEC-04 — Architecture

## Layers

```
┌─────────────────────────────────────┐
│           Display (crossterm)       │  renders state → no logic
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
- Plain Rust struct; no side effects; updated only by the controller

**Filesystem adapter**
- Lists directory contents (`std::fs::read_dir`)
- Reads file metadata (`std::fs::metadata`)
- Handles permission errors (`io::Error`)
- Has no knowledge of navigation or display

**Navigation / Controller**
- Reads keyboard events via crossterm (`event::read`)
- Calls the filesystem adapter
- Mutates state
- Contains no rendering code
- Puts the terminal in raw mode; restores it on exit or panic

**Display (crossterm)**
- Renders state into three columns using `crossterm::execute!` / `queue!`
- Applies ANSI colors and Unicode box-drawing characters
- Minimum contract: `render(state: &AppState)`
- Does not modify state or access the filesystem

## Decoupling rules

- Display ← does not call filesystem or modify state
- Controller ← does not know rendering details
- Filesystem adapter ← does not know about navigation or display

## Extensibility

The architecture allows — without changing navigation or state:
- Swapping the display backend (e.g. crossterm → ratatui → other)
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

- Rust (stable, current edition)
- [crossterm](https://github.com/crossterm-rs/crossterm) for raw terminal control, keyboard input, cursor movement, and ANSI color
- `std::fs` for all filesystem access
- No GUI or TUI framework dependencies
