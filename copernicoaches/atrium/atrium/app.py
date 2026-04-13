from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual import events
from textual.widgets import Static

from .controller import NavigationController
from .display import DisplayRenderer
from .filesystem import FilesystemAdapter


class AtriumApp(App[None]):
    BINDINGS = [
        Binding("up", "move_up", "Up"),
        Binding("down", "move_down", "Down"),
        Binding("left", "go_parent", "Parent"),
        Binding("backspace", "go_parent", "Parent"),
        Binding("right", "enter_selection", "Enter"),
        Binding("enter", "enter_selection", "Enter"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    #display {
        height: 1fr;
        padding: 1 2;
    }
    """

    def __init__(
        self,
        *,
        start_path: Path | None = None,
        filesystem: FilesystemAdapter | None = None,
    ) -> None:
        super().__init__()
        self.controller = NavigationController(start_path=start_path, filesystem=filesystem)
        self.renderer = DisplayRenderer()
        self.last_rendered = ""

    def compose(self) -> ComposeResult:
        yield Static("", id="display", markup=False)

    def on_mount(self) -> None:
        self.refresh_display()

    def action_move_up(self) -> None:
        self.controller.move_up()
        self.refresh_display()

    def action_move_down(self) -> None:
        self.controller.move_down()
        self.refresh_display()

    def action_enter_selection(self) -> None:
        if self.controller.enter_selection():
            self.renderer.reset_center_scroll()
        self.refresh_display()

    def action_go_parent(self) -> None:
        if self.controller.go_parent():
            self.renderer.reset_center_scroll()
        self.refresh_display()

    def on_resize(self, event: events.Resize) -> None:
        self.refresh_display()

    def refresh_display(self) -> None:
        viewport_height = max(1, self.size.height - 6)
        state = self.controller.build_display_state(viewport_height=viewport_height)
        rendered = self.renderer.render(state, viewport_height=viewport_height)
        self.last_rendered = rendered
        self.query_one("#display", Static).update(rendered)
