from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atrium import DirectoryListing, NavigationController
from atrium.models import Entry


class FakeFilesystem:
    def __init__(self, listings: dict[Path, DirectoryListing]) -> None:
        self.listings = listings

    def list_directory(self, path: Path) -> DirectoryListing:
        return self.listings[path.resolve()]


class Spec02NavigationTests(unittest.TestCase):
    def test_vertical_movement_updates_selection_and_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "alpha").mkdir()
            (root / "beta").mkdir()

            controller = NavigationController(start_path=root)

            self.assertEqual(controller.state.selected.name, "alpha")
            controller.move_down()
            self.assertEqual(controller.state.selected.name, "beta")
            self.assertEqual(controller.state.preview_target, controller.state.selected)
            controller.move_up()
            self.assertEqual(controller.state.selected.name, "alpha")

    def test_enter_directory_loads_it_as_the_new_center_column(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            child = root / "child"
            child.mkdir()
            (child / "inside.txt").write_text("hello", encoding="utf-8")

            controller = NavigationController(start_path=root)

            self.assertTrue(controller.enter_selection())
            self.assertEqual(controller.state.parent_dir, root)
            self.assertEqual(controller.state.current_dir, child)
            self.assertEqual([entry.name for entry in controller.state.current_entries], ["inside.txt"])
            self.assertEqual(controller.state.selected.name, "inside.txt")

    def test_enter_on_file_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            file_path = root / "note.txt"
            file_path.write_text("hello", encoding="utf-8")

            controller = NavigationController(start_path=root)
            before = controller.state.current_dir

            self.assertFalse(controller.enter_selection())
            self.assertEqual(controller.state.current_dir, before)
            self.assertEqual(controller.state.selected.path, file_path.resolve())

    def test_returning_to_parent_restores_the_directory_just_exited(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first"
            second = root / "second"
            first.mkdir()
            second.mkdir()
            (first / "child.txt").write_text("hello", encoding="utf-8")

            controller = NavigationController(start_path=root)
            self.assertTrue(controller.enter_selection())

            self.assertTrue(controller.go_parent())
            self.assertEqual(controller.state.current_dir, root)
            self.assertEqual(controller.state.selected.path, first.resolve())
            self.assertEqual(controller.state.preview_target.path, first.resolve())

    def test_root_navigation_is_stable(self) -> None:
        controller = NavigationController(start_path=Path("/"))
        before = controller.state.current_dir

        self.assertFalse(controller.go_parent())
        self.assertEqual(controller.state.current_dir, before)
        self.assertIsNone(controller.state.parent_dir)

    def test_permission_error_is_captured_without_breaking_navigation(self) -> None:
        root = Path("/virtual")
        denied = root / "denied"
        sibling = root / "sibling"
        listings = {
            root: DirectoryListing(
                path=root,
                entries=(
                    Entry(name="denied", path=denied, is_dir=True),
                    Entry(name="sibling", path=sibling, is_dir=True),
                ),
            ),
            denied: DirectoryListing(path=denied, entries=(), error="Permission denied"),
            sibling: DirectoryListing(path=sibling, entries=()),
        }
        controller = NavigationController(start_path=root, filesystem=FakeFilesystem(listings))

        self.assertTrue(controller.enter_selection())
        self.assertEqual(controller.state.current_dir, denied)
        self.assertEqual(controller.state.current_entries, ())
        self.assertEqual(controller.state.current_error, "Permission denied")
        self.assertIsNone(controller.state.selected)
        self.assertTrue(controller.go_parent())
        self.assertEqual(controller.state.current_dir, root)
        self.assertEqual(controller.state.current_error, None)


if __name__ == "__main__":
    unittest.main()
