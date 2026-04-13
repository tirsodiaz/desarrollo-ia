# SPEC-05 — Viewport-Safe Scrolling

## Objective

When the selected item moves in a column, the rendered list must always keep the selected item visible inside the available terminal height.

The display must render only the visible slice for the current viewport — not the full item list.

Do not change business logic, file system behavior, keyboard mappings, navigation state, or overall application structure. Only change the display pipeline and where viewport state is tracked.

---

## Current implementation gap

The current code renders all rows without viewport clipping:

- `DisplayColumn` dataclass has no `selected_index`
- `render_display` iterates `range(max_rows)` unconditionally
- `DisplayRenderer.render` has no knowledge of terminal height
- `NavigationController.build_display_state` passes no viewport height
- `AtriumApp` has no `on_resize` handler to trigger re-renders on terminal resize

All of these must change.

---

## Required changes

### 1. `DisplayColumn` — add `selected_index`

`DisplayColumn` must carry one additional field:

| Field            | Type            | Meaning                                                                    |
|------------------|-----------------|----------------------------------------------------------------------------|
| `selected_index` | `Optional[int]` | Index of the highlighted row within `rows`; `None` if nothing is selected  |

The dataclass remains `frozen=True`. `selected_index` defaults to `None`.

`selected_index` supplements the implicit `row.highlighted` flag. The scroll logic uses the numeric index; `highlighted` may remain for coloring.

`scroll_offset` is **not** added to `DisplayColumn` — it is renderer state and must not enter the frozen dataclass.

---

### 2. Viewport state — where it lives

`scroll_offset` is not navigation state and must not be stored in `AtriumState`.

`scroll_offset` must persist across renders for the **center column** (it must not reset on every redraw). It is reset to `0` only when the directory changes.

`scroll_offset` for **left and right columns** is computed fresh each render from `selected_index` (see §4 below); it does not need to persist.

**Owner:** `DisplayRenderer` gains an instance attribute `_center_scroll_offset: int = 0`. It is the only place this value is stored. The renderer updates it each time it computes the visible slice for the center column.

---

### 3. Terminal height

`viewport_height` must be derived from the live terminal dimensions, not hardcoded.

- Textual exposes the current terminal dimensions via `self.size.height` on any `App` or `Widget` subclass
- Fixed overhead rows to subtract from the terminal height:
  - Path line: 1 row
  - Blank line after path: 1 row
  - Column header row: 1 row
  - Separator row: 1 row
  - CSS padding on `#display` (`padding: 1 2`): 2 rows (top + bottom)
  - **Total overhead: 6 rows**
- `viewport_height = max(1, self.size.height - 6)`

`AtriumApp.refresh_display` must obtain `viewport_height` from Textual before calling `build_display_state`, so that every re-render reflects the current terminal size. The result is not stored; it is computed fresh every call.

---

### 4. Scroll update algorithm

Apply this algorithm when computing which rows to render for a column:

```text
given: items, selected_index, scroll_offset, viewport_height

if selected_index < scroll_offset:
    scroll_offset = selected_index                         # scroll up

if selected_index >= scroll_offset + viewport_height:
    scroll_offset = selected_index - viewport_height + 1  # scroll down

scroll_offset = max(0, min(scroll_offset, len(items) - viewport_height))
visible_slice = items[scroll_offset : scroll_offset + viewport_height]
```

- Scroll only when needed.
- Do not re-center on every move.

For **left and right columns**, start with `scroll_offset = 0` and apply the algorithm before rendering (it is not persisted — just computed per render call).

For the **center column**, read `self._center_scroll_offset`, apply the algorithm, then write the result back to `self._center_scroll_offset`.

---

### 5. `NavigationController.build_display_state`

Must accept a `viewport_height: int` keyword argument in addition to `column_width: int`.

Each `DisplayColumn` it produces must include `selected_index` (the position of the highlighted entry in `rows`, or `None` when there is no selection or the column is empty).

`build_display_state` does **not** compute `scroll_offset`; that is the renderer's responsibility.

---

### 6. `DisplayRenderer.render` and `render_display`

`DisplayRenderer.render` must accept `viewport_height: int` and forward it to the rendering logic.

`render_display` (the standalone function) must also accept `viewport_height: int`. It applies the scroll algorithm per column and renders only the visible slice. Padding empty rows are added so all columns always reach `viewport_height` rows, maintaining alignment.

Steps on every render call:

1. Receive `state: DisplayState` and `viewport_height: int`.
2. For each column, compute `selected_index` from `column.selected_index`.
3. For center column: run the scroll algorithm against `self._center_scroll_offset`; write the result back.
4. For left and right columns: run the scroll algorithm starting from `scroll_offset = 0`.
5. Slice each column's `rows` to the visible window.
6. Pad all columns with empty rows to `viewport_height` so alignment is maintained.
7. Render only the visible slice.

For **tests**, call `render_display(state, viewport_height=N)` with a fixed integer — no terminal is queried, so tests remain deterministic.

---

### 7. `_center_scroll_offset` reset

Reset `_center_scroll_offset` to `0` on `AtriumApp` whenever the controller changes `current_dir`:

- after `action_enter_selection`
- after `action_go_parent`

`AtriumApp` owns both the controller and the renderer, so it is the right place for this reset.

---

### 8. Resize handling in Textual

Override `on_resize` in `AtriumApp` to call `refresh_display`:

```python
def on_resize(self, event: events.Resize) -> None:
    self.refresh_display()
```

No other resize handling is required; `refresh_display` already queries `self.size.height` fresh on each call.

---

## Acceptance criteria

- The selected item is always visible in all three columns
- Moving down beyond the bottom of the visible area scrolls the list down by one row
- Moving up beyond the top of the visible area scrolls the list up by one row
- The list does not jump or re-center when the selection is already visible
- Resizing the terminal adjusts the visible area without breaking selection visibility
- Entering or leaving a directory resets the center column scroll offset to `0`
- `render_display(state, viewport_height=N)` in tests accepts a fixed height and remains deterministic
- Only display / viewport behavior changes; navigation semantics are unchanged

---

## Example

Terminal height = 20 rows. Overhead = 6. `viewport_height` = 14.

Directory has 25 entries. User navigates down to entry 14 (index 13, zero-based):

```text
scroll_offset = 0   → entry 13 is within [0..14) → no scroll needed
```

User navigates to entry 15 (index 14):

```text
scroll_offset = 1   → entry 14 is now last visible row
```

User navigates back to entry 14 (index 13):

```text
scroll_offset = 1   → entry 13 is still visible at row 12 of 14 → no scroll
```
