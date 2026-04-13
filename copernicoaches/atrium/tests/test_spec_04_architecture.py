from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atrium import AtriumApp, DisplayRenderer


class Spec04ArchitectureTests(unittest.IsolatedAsyncioTestCase):
    def test_display_renderer_is_pure_projection(self) -> None:
        renderer = DisplayRenderer()
        state = AtriumApp(start_path=Path("/")).controller.build_display_state(
            column_width=16,
            viewport_height=8,
        )

        first = renderer.render(state, viewport_height=8)
        second = renderer.render(state, viewport_height=8)

        self.assertEqual(first, second)

    async def test_textual_app_updates_from_controller_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "alpha").mkdir()
            (root / "beta").mkdir()

            app = AtriumApp(start_path=root)
            async with app.run_test() as pilot:
                await pilot.pause()
                self.assertIn("▶ 📁 alpha", app.last_rendered)

                await pilot.press("down")
                await pilot.pause()
                self.assertIn("▶ 📁 beta", app.last_rendered)

    async def test_textual_app_preserves_literal_prefixes_in_rendered_widget(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            current = parent / "current"
            child = current / "child"
            sibling = parent / "sibling.txt"
            current.mkdir()
            child.mkdir()
            sibling.write_text("other", encoding="utf-8")

            app = AtriumApp(start_path=current)
            async with app.run_test(size=(120, 12)) as pilot:
                await pilot.pause()
                widget = app.query_one("#display")
                first_body_row = "".join(segment.text for segment in widget.render_line(4))

                self.assertIn("▶ 📁 current", first_body_row)
                self.assertIn("▶ 📁 child", first_body_row)
                self.assertEqual(first_body_row, app.last_rendered.splitlines()[4])

    async def test_textual_app_enters_directory_and_returns_to_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            child = root / "child"
            child.mkdir()
            (child / "inside.txt").write_text("payload", encoding="utf-8")

            app = AtriumApp(start_path=root)
            async with app.run_test() as pilot:
                await pilot.pause()
                await pilot.press("enter")
                await pilot.pause()
                self.assertIn(str(child.resolve()), app.last_rendered)
                self.assertIn("▶ 📄 inside.txt", app.last_rendered)

                await pilot.press("left")
                await pilot.pause()
                self.assertIn(str(root.resolve()), app.last_rendered)
                self.assertIn("▶ 📁 child", app.last_rendered)


if __name__ == "__main__":
    unittest.main()
