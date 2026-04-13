from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from textual.events import Resize

from atrium import AtriumApp, DisplayRenderer, NavigationController


VIEWPORT_HEIGHT = 4


def _column_rows(rendered: str, column_index: int) -> list[str]:
    return [line.split("│")[column_index].strip() for line in rendered.splitlines()[4:]]


class Spec05StableViewportTests(unittest.IsolatedAsyncioTestCase):
    def test_renderer_clips_body_to_viewport_height(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index in range(10):
                (root / f"dir-{index:02d}").mkdir()

            renderer = DisplayRenderer()
            controller = NavigationController(start_path=root)
            rendered = renderer.render(
                controller.build_display_state(column_width=18, viewport_height=VIEWPORT_HEIGHT),
                viewport_height=VIEWPORT_HEIGHT,
            )

            self.assertEqual(len(rendered.splitlines()), VIEWPORT_HEIGHT + 4)

    def test_moving_down_scrolls_only_when_selection_leaves_viewport(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index in range(8):
                (root / f"dir-{index:02d}").mkdir()

            renderer = DisplayRenderer()
            controller = NavigationController(start_path=root)

            initial = renderer.render(
                controller.build_display_state(column_width=18, viewport_height=VIEWPORT_HEIGHT),
                viewport_height=VIEWPORT_HEIGHT,
            )
            initial_rows = _column_rows(initial, 2)
            self.assertIn("▶ 📁 dir-00", initial_rows[0])
            self.assertIn("dir-03", initial_rows[3])

            for _ in range(3):
                controller.move_down()
            still_visible = renderer.render(
                controller.build_display_state(column_width=18, viewport_height=VIEWPORT_HEIGHT),
                viewport_height=VIEWPORT_HEIGHT,
            )
            still_visible_rows = _column_rows(still_visible, 2)
            self.assertIn("dir-00", still_visible_rows[0])
            self.assertIn("▶ 📁 dir-03", still_visible_rows[3])

            controller.move_down()
            scrolled = renderer.render(
                controller.build_display_state(column_width=18, viewport_height=VIEWPORT_HEIGHT),
                viewport_height=VIEWPORT_HEIGHT,
            )
            scrolled_rows = _column_rows(scrolled, 2)
            self.assertIn("dir-01", scrolled_rows[0])
            self.assertIn("▶ 📁 dir-04", scrolled_rows[3])

            controller.move_up()
            no_recentering = renderer.render(
                controller.build_display_state(column_width=18, viewport_height=VIEWPORT_HEIGHT),
                viewport_height=VIEWPORT_HEIGHT,
            )
            no_recentering_rows = _column_rows(no_recentering, 2)
            self.assertIn("dir-01", no_recentering_rows[0])
            self.assertIn("▶ 📁 dir-03", no_recentering_rows[2])

    def test_left_column_computes_visibility_from_highlighted_path_each_render(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            for index in range(8):
                (parent / f"dir-{index:02d}").mkdir()
            current = parent / "dir-06"

            renderer = DisplayRenderer()
            controller = NavigationController(start_path=current)
            rendered = renderer.render(
                controller.build_display_state(column_width=18, viewport_height=VIEWPORT_HEIGHT),
                viewport_height=VIEWPORT_HEIGHT,
            )
            left_rows = _column_rows(rendered, 1)

            self.assertTrue(any("▶ 📁 dir-06" in row for row in left_rows))

    async def test_entering_and_leaving_directory_resets_center_scroll(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            child = root / "child"
            child.mkdir()
            for index in range(8):
                (root / f"dir-{index:02d}").mkdir()
                (child / f"file-{index:02d}.txt").write_text("payload", encoding="utf-8")

            app = AtriumApp(start_path=root)
            async with app.run_test(size=(120, 10)) as pilot:
                await pilot.pause()
                for _ in range(4):
                    await pilot.press("down")
                    await pilot.pause()

                scrolled_rows = _column_rows(app.last_rendered, 2)
                self.assertIn("dir-00", scrolled_rows[0])

                while app.controller.state.selected and app.controller.state.selected.name != "child":
                    await pilot.press("up")
                    await pilot.pause()

                await pilot.press("enter")
                await pilot.pause()
                entered_rows = _column_rows(app.last_rendered, 2)
                self.assertIn("▶ 📄 file-00.txt", entered_rows[0])

                await pilot.press("left")
                await pilot.pause()
                returned_rows = _column_rows(app.last_rendered, 2)
                self.assertIn("▶ 📁 child", returned_rows[0])

    async def test_resize_refreshes_using_new_viewport_height(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index in range(8):
                (root / f"dir-{index:02d}").mkdir()

            app = AtriumApp(start_path=root)
            async with app.run_test(size=(120, 10)) as pilot:
                await pilot.pause()
                self.assertEqual(len(app.last_rendered.splitlines()), 8)

                app._size = app.size.__class__(120, 12)
                app.on_resize(Resize(size=app.size, virtual_size=app.size))
                await pilot.pause()

                self.assertEqual(len(app.last_rendered.splitlines()), 10)
