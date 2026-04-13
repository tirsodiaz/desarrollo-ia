from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rich.cells import cell_len

from atrium import NavigationController, render_display


class Spec03DisplayTests(unittest.TestCase):
    def test_display_state_contains_parent_current_and_directory_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            current = parent / "current"
            sibling = parent / "sibling.txt"
            child = current / "child"
            current.mkdir()
            child.mkdir()
            sibling.write_text("other", encoding="utf-8")
            (child / "nested.txt").write_text("nested", encoding="utf-8")

            controller = NavigationController(start_path=current)
            display = controller.build_display_state(viewport_height=8)

            self.assertEqual(display.current_path, str(current.resolve()))
            self.assertTrue(display.center.emphasized)
            self.assertEqual(display.left.selected_index, 0)
            self.assertEqual([row.text for row in display.left.rows], ["current", "sibling.txt"])
            self.assertTrue(display.left.rows[0].highlighted)
            self.assertEqual([row.text for row in display.center.rows], ["child"])
            self.assertTrue(display.center.rows[0].highlighted)
            self.assertEqual(display.center.selected_index, 0)
            self.assertEqual([row.text for row in display.right.rows], ["nested.txt"])
            self.assertIsNone(display.right.selected_index)

    def test_file_selection_shows_metadata_and_text_excerpt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            note = root / "note.txt"
            note.write_text("line one\nline two\nline three\n", encoding="utf-8")

            controller = NavigationController(start_path=root)
            display = controller.build_display_state(viewport_height=8)

            self.assertEqual([row.text for row in display.right.rows[:3]], [
                "Name: note.txt",
                "Type: txt",
                "Size: 29 B",
            ])
            self.assertEqual([row.text for row in display.right.rows[3:]], ["line one", "line two", "line three"])

    def test_none_selection_keeps_preview_blank(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            controller = NavigationController(start_path=Path(temp_dir))
            display = controller.build_display_state(viewport_height=8)

            self.assertEqual(display.right.rows, ())

    def test_rendered_output_exposes_current_path_and_fixed_width_columns(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "alpha").mkdir()

            controller = NavigationController(start_path=root)
            rendered = render_display(
                controller.build_display_state(column_width=18, viewport_height=8),
                viewport_height=8,
            )

            lines = rendered.splitlines()
            self.assertIn(str(root.resolve()), lines[0])
            self.assertEqual(lines[1], "")
            self.assertEqual(cell_len(lines[2]), cell_len(lines[3]))
            self.assertEqual(cell_len(lines[2]), cell_len(lines[4]))
            self.assertIn("[* Current *]", lines[2])
            self.assertIn("📁 alpha", lines[4])
            separator_positions = _separator_positions(lines[2])
            self.assertEqual(
                separator_positions,
                _separator_positions(lines[4]),
            )


def _separator_positions(line: str) -> list[int]:
    return [cell_len(line[:index]) for index, char in enumerate(line) if char == "│"]


if __name__ == "__main__":
    unittest.main()
