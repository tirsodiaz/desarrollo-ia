# Prompt — UI Rendering Upgrade (Console, Unicode)

Refactor the console rendering layer only. Do not change any application logic, navigation behavior, data structures, or state management.

### Objective

Transform the current ASCII-based interface into a more readable and visually structured console UI using Unicode characters and minimal iconography.

The application must continue to behave exactly the same. Only the visual representation changes.

---

### Scope (strict)

You are allowed to modify only:

* rendering / printing functions
* formatting of strings
* characters used for borders, separators, and markers
* visual indicators (icons, prefixes, highlights)

You are NOT allowed to modify:

* navigation logic
* file system access
* data models
* selection behavior
* keyboard handling
* pipeline or business logic

---

### Visual requirements

#### 1. Column structure

Maintain the three-column Miller layout:

* Parent
* Current
* Preview

Replace plain ASCII separators with Unicode box-drawing characters:

* vertical separator → `│`
* optional horizontal separators → `─`
* corners (if used) → `┌ ┐ └ ┘`

Columns must remain aligned and fixed-width.

---

#### 2. File and directory indicators

Replace `[D]` and `[F]` with icons:

* directory → `📁`
* file → `📄`

Keep them simple and consistent.

Example:

```
📁 atrium
📄 README.md
```

---

#### 3. Selection indicator

Keep a single clear selection marker.

Replace `>` with a more visual indicator:

* `▶` or `➜`

Example:

```
▶ 📁 images
```

Do not combine multiple selection indicators.

---

#### 4. Current column emphasis

The current column should be visually distinguished:

* header remains `[ * Current * ]`
* optionally use brighter color or subtle emphasis (if color already exists)
* do not add structural complexity

---

#### 5. Path display

Keep the path at the top.

Optionally improve readability using:

```
Path: /Users/ivanderk/src/copernicoaches/atrium
```

No structural changes required.

---

#### 6. Spacing and readability

* ensure consistent padding inside columns
* avoid overcrowding
* truncate long filenames with `…` if needed
* maintain vertical alignment across all rows

---

### Example target style

```
Path: /Users/ivanderk/src/copernicoaches/atrium

│ Parent                    │ [* Current *]            │ Preview               │
│──────────────────────────│──────────────────────────│──────────────────────│
│ 📁 .claude               │ ▶ 📁 .venv               │ 📁 bin                │
│ 📁 .git                  │   📁 atrium              │ 📁 lib                │
│ 📁 .github               │   📁 images              │ 📄 .gitignore         │
│ 📁 .vscode               │   📁 specs               │ 📄 .lock              │
│ 📁 ac_checkaccount...    │   📁 tests               │ 📄 CACHEDIR.TAG       │
│ ▶ 📁 atrium              │   📄 pyproject.toml      │ 📄 pyvenv.cfg         │
│ 📁 dia1                  │   📄 README.md           │                       │
│ 📁 dia2                  │   📄 uv.lock             │                       │
```

---

### Constraints

* Output must remain pure console (no GUI libraries)
* Must work in standard terminal environments
* Unicode usage must degrade gracefully if unsupported
* No dependency on external UI frameworks

---

### Acceptance criteria

* Navigation behaves exactly as before
* Data shown is identical
* Only visual representation changes
* Columns are clearly separated and aligned
* Interface is more readable and visually structured

