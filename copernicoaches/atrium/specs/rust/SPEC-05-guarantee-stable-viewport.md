# SPEC-05 — Viewport-Safe Scrolling

## Objective

When the selected item moves in a column, the rendered list must always keep the selected item visible inside the available terminal height.

The display must render only the visible slice for the current viewport — not the full item list.

Do not change business logic, file system behavior, keyboard mappings, navigation state, or overall application structure. Only change the display pipeline and where viewport state is tracked.

---

## Current implementation gap

The current code renders all rows without viewport clipping:

- `DisplayColumn` has no `scroll_offset` or `selected_index`
- `RenderLayout::from_state` iterates `0..max_rows` unconditionally
- `DisplayRenderer` tracks only `column_width`; it has no knowledge of terminal height
- `NavigationController::build_display_state` passes no terminal dimensions
- `app.rs` handles `Event::Resize` but does not forward terminal height to the renderer

All of these must change.

---

## Required changes

### 1. `DisplayColumn` — add viewport fields

`DisplayColumn` must carry two additional fields:

| Field            | Type            | Meaning                                                                    |
|------------------|-----------------|----------------------------------------------------------------------------|
| `selected_index` | `Option<usize>` | Index of the highlighted row within `rows`; `None` if nothing is selected |
| `scroll_offset`  | `usize`         | Index of the first visible row                                             |

`selected_index` replaces the implicit `row.highlighted` for scroll calculations. `highlighted` may remain for coloring, but the scroll logic must use the numeric index.

---

### 2. Viewport state — where it lives

`scroll_offset` is not navigation state and must not be stored in `AppState`.

`scroll_offset` must persist across renders for the **center column** (it must not reset on every redraw). It is reset to `0` only when the directory changes.

`scroll_offset` for **left and right columns** is computed fresh each render from `selected_index` (see §4 below); it does not need to persist.

**Owner:** `DisplayRenderer` holds a `center_scroll_offset: usize`. It is the only place this value is stored. The renderer updates it each time it computes the visible slice for the center column.

---

### 3. Terminal height

`viewport_height` must be derived from the live terminal dimensions, not hardcoded.

- Use `crossterm::terminal::size()` → `(cols, rows)`
- Fixed UI overhead per render (subtract from `rows`):
  - Path line: 1 row
  - Blank line after path: 1 row
  - Column header row: 1 row
  - Separator row: 1 row
  - **Total overhead: 4 rows**
- `viewport_height = terminal_rows.saturating_sub(4)`

`DisplayRenderer::render` must query terminal size at the start of each render call. The result is not stored; it is computed fresh every render so that `Event::Resize` is handled automatically.

---

### 4. Scroll update algorithm

Apply this algorithm when computing which rows to render for a column:

```text
given: items, selected_index, scroll_offset, viewport_height

if selected_index < scroll_offset:
    scroll_offset = selected_index          // scroll up

if selected_index >= scroll_offset + viewport_height:
    scroll_offset = selected_index - viewport_height + 1   // scroll down

visible_slice = items[scroll_offset .. scroll_offset + viewport_height]
```

- Scroll only when needed.
- Do not re-center on every move.
- `scroll_offset` is clamped to `0..items.len().saturating_sub(viewport_height)`.

For **left and right columns**, `scroll_offset` starts at `0` and is adjusted by the algorithm above before rendering (it is not persisted — just computed per render).

For the **center column**, `scroll_offset` is read from `DisplayRenderer.center_scroll_offset`, updated by the algorithm, then written back.

---

### 5. `NavigationController::build_display_state`

Must accept `viewport_height: usize` in addition to `column_width: usize`.

Each `DisplayColumn` it produces must include `selected_index` (the position of the highlighted entry in `rows`).

`build_display_state` does **not** compute `scroll_offset`; that is the renderer's responsibility.

---

### 6. `DisplayRenderer::render`

Steps at the start of every render:

1. Call `crossterm::terminal::size()` to obtain `(cols, rows)`.
2. Compute `viewport_height = rows.saturating_sub(4)`.
3. Call `controller.build_display_state(column_width, viewport_height)` (or accept a pre-built `DisplayState` with `viewport_height` set).
4. For center column: run the scroll algorithm against `self.center_scroll_offset` and update it.
5. For left and right columns: run the scroll algorithm starting from offset `0`.
6. Render only `visible_slice` for each column.
7. Pad all columns to `viewport_height` rows with empty cells so alignment is maintained.

`render_to_string` (used in tests) must accept an explicit `viewport_height` parameter rather than querying the terminal, so tests remain deterministic.

---

### 7. `center_scroll_offset` reset

Reset `center_scroll_offset` to `0` whenever `NavigationController` changes `current_dir`:

- on `enter_selection`
- on `go_parent`

This is a responsibility of `AtriumApp`, which owns both the controller and the renderer.

---

### 8. `Event::Resize` in `app.rs`

`Event::Resize` already triggers a re-render. No additional handling is required because `render` queries terminal size fresh on each call.

---

## Acceptance criteria

- The selected item is always visible in all three columns
- Moving down beyond the bottom of the visible area scrolls the list down by one row
- Moving up beyond the top of the visible area scrolls the list up by one row
- The list does not jump or re-center when the selection is already visible
- Resizing the terminal adjusts the visible area without breaking selection visibility
- Entering or leaving a directory resets the center column scroll offset to `0`
- `render_to_string` in tests accepts a fixed `viewport_height` and remains deterministic
- Only display / viewport behavior changes; navigation semantics are unchanged

---

## Example

Terminal height = 14 rows. Overhead = 4. `viewport_height` = 10.

Directory has 25 entries. User navigates down to entry 10 (index 9, zero-based):

```text
scroll_offset = 0   → entry 9 is within [0..10) → no scroll needed
```

User navigates to entry 11 (index 10):

```text
scroll_offset = 1   → entry 10 is now first visible row
```

User navigates back to entry 10 (index 9):

```text
scroll_offset = 1   → entry 9 is still visible at row 8 of 10 → no scroll
```
