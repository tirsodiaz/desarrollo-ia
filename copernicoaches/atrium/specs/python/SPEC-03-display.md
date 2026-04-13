# SPEC-03 — Display

## Layout

Three fixed-width columns rendered simultaneously:

| Column  | Content |
|---------|---------|
| Left    | Contents of `parent_dir`; `current_dir` highlighted |
| Center  | Contents of `current_dir`; `selected` highlighted; always has focus |
| Right   | Preview of `selected` (see rules below) |

The center column is visually dominant (focus indicator, stronger styling).

## Right column rules

| `selected` type | Right column shows |
|-----------------|--------------------|
| Directory       | List of its contents |
| File            | Name, type, size; first lines if plain text |
| None            | Empty |

## Visual rules

- Directories and files are visually distinct (color or prefix)
- Selected entry is clearly highlighted
- Current path is always visible (header or status bar)
- Column widths are consistent and aligned
- Colors are used for: selection, entry type

## Behaviour contract

The display layer:
- receives state, never modifies it
- does not access the filesystem directly
- updates fully on every state change

## Principle

> The display is simple, textual, and sufficient to understand the complete system state at any moment.
