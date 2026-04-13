from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atrium import build_initial_state


class Spec01OverviewTests(unittest.TestCase):
    def test_initial_state_defaults_to_working_directory(self) -> None:
        initial = build_initial_state()

        self.assertEqual(initial.current_dir, Path.cwd().resolve())
        self.assertEqual(initial.parent_dir, Path.cwd().resolve().parent)

    def test_first_entry_is_selected_automatically(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "b-file.txt").write_text("payload", encoding="utf-8")
            (root / "a-dir").mkdir()

            initial = build_initial_state(root)

            self.assertEqual([entry.name for entry in initial.current_entries], ["a-dir", "b-file.txt"])
            self.assertIsNotNone(initial.selected)
            self.assertEqual(initial.selected.name, "a-dir")
            self.assertEqual(initial.preview_target, initial.selected)

    def test_empty_directory_has_no_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            initial = build_initial_state(Path(temp_dir))

            self.assertEqual(initial.current_entries, ())
            self.assertIsNone(initial.selected)
            self.assertIsNone(initial.preview_target)


if __name__ == "__main__":
    unittest.main()
