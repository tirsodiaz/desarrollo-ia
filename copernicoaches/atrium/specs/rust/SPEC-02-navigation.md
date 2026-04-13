# SPEC-02 — Navigation Model

## State

The system maintains a single source of truth at all times:

| Field             | Description                              |
|-------------------|------------------------------------------|
| `current_dir`     | The directory currently in focus         |
| `parent_dir`      | Parent of `current_dir`                  |
| `current_entries` | Contents of `current_dir`                |
| `selected`        | Currently highlighted entry              |
| `preview_target`  | Entry whose content fills the right column |

The three columns are derived views of this state.

## Startup

- `current_dir` defaults to the process working directory
- First entry in `current_dir` is selected automatically
- If `current_dir` is empty, `selected` is `None` and the right column is blank

## Navigation rules

### Vertical movement (↑ / ↓)

- Moves `selected` within `current_dir`
- `preview_target` updates immediately

### Enter directory (→ or Enter)

Only valid when `selected` is a directory.

| Before        | After           |
|---------------|-----------------|
| left  ← parent | left  ← old current |
| center ← current | center ← selected dir |
| right ← preview | right ← contents of new current |

### Go to parent (← or Backspace)

| Before        | After           |
|---------------|-----------------|
| left ← grandparent | left ← new grandparent |
| center ← parent | center ← old parent |
| right ← current | right ← old current |

Selection in the new center column is restored to the directory just exited.

### Quit (q or Ctrl-C)

Exit the application and restore the terminal to its original state.

## Edge cases

| Situation            | Behaviour |
|----------------------|-----------|
| Empty directory      | No selection; right column is blank |
| File selected        | Right column shows metadata; → is ignored |
| At filesystem root   | Left column is empty; system stays stable |
| Permission error     | Column shows error indicator; navigation continues |
