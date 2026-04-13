# SPEC-03 — Display

## Layout

Three fixed-width columns rendered simultaneously:

| Column  | Content |
|---------|---------|
| Left    | Contents of `parent_dir`; `current_dir` highlighted |
| Center  | Contents of `current_dir`; `selected` highlighted; always has focus |
| Right   | Preview of `selected` (see rules below) |

The center column is visually dominant (header emphasis, brighter styling via ANSI color).

## Column structure

Columns are separated by Unicode box-drawing characters:

- Vertical separator: `│`
- Horizontal separator (under headers): `─`
- Corners (if used): `┌ ┐ └ ┘`

Columns must remain aligned and fixed-width. Long filenames are truncated with `…`.

## Column headers

```
│ Parent                    │ [* Current *]            │ Preview               │
│──────────────────────────│──────────────────────────│──────────────────────│
```

## Right column rules

| `selected` type | Right column shows |
|-----------------|--------------------|
| Directory       | List of its contents |
| File            | Name, type, size; first lines if plain text |
| None            | Empty |

## Entry indicators

Each entry is prefixed with a type icon:

- Directory: `📁`
- File: `📄`

The selected entry in the center column is prefixed with `▶`:

```
▶ 📁 images
  📄 README.md
```

In non-center columns, the entry corresponding to the active path is also prefixed with `▶`.

## Path display

Current path displayed at the top of the screen:

```
Path: /Users/ivanderk/src/copernicoaches/atrium
```

## Example target style

```
Path: /Users/ivanderk/src/copernicoaches/atrium

│ Parent                    │ [* Current *]            │ Preview               │
│──────────────────────────│──────────────────────────│──────────────────────│
│ 📁 .claude               │ ▶ 📁 .venv               │ 📁 bin                │
│ 📁 .git                  │   📁 atrium              │ 📁 lib                │
│ 📁 .github               │   📁 images              │ 📄 .gitignore         │
│ 📁 .vscode               │   📁 specs               │ 📄 .lock              │
│ 📁 ac_checkaccount…      │   📁 tests               │ 📄 CACHEDIR.TAG       │
│ ▶ 📁 atrium              │   📄 pyproject.toml      │ 📄 pyvenv.cfg         │
│ 📁 dia1                  │   📄 README.md           │                       │
│ 📁 dia2                  │   📄 uv.lock             │                       │
```

## Visual rules

- Directories and files are visually distinct (icon prefix)
- Selected entry is clearly highlighted (ANSI color + `▶` marker)
- Current path is always visible at the top
- Column widths are consistent and aligned
- ANSI colors are used for: selection highlight, entry type, current column emphasis
- Unicode usage degrades gracefully if the terminal does not support it

## Behaviour contract

The display layer:
- receives state, never modifies it
- does not access the filesystem directly
- re-renders fully on every state change
- restores the terminal to its original state on exit

## Constraints

- Output must remain pure console (no GUI libraries)
- Must work in standard terminal environments
- No dependency on external TUI frameworks

## Principle

> The display is simple, textual, and sufficient to understand the complete system state at any moment.
