"""Tests de integración del bucle principal."""

from pathlib import Path

from miller.__main__ import run_app
from miller.state.model import AppState, FileEntry


class FakeRenderer:
    def __init__(self):
        self.rendered_indexes: list[int] = []
        self.rendered_states: list[AppState] = []

    def render(self, state: AppState, terminal_size=None):
        self.rendered_indexes.append(state.selected_index)
        self.rendered_states.append(state)


class FakeNavigator:
    def __init__(self, initial_state: AppState):
        self.state = initial_state
        self.refresh_calls = 0

    def initialize(self) -> AppState:
        return self.state

    def refresh(self, state: AppState) -> AppState:
        self.refresh_calls += 1
        return state

    def move_up(self, state: AppState) -> AppState:
        if state.selected_index > 0:
            state.selected_index -= 1
        return state

    def move_down(self, state: AppState) -> AppState:
        if state.selected_index < len(state.current_contents) - 1:
            state.selected_index += 1
        return state

    def enter_directory(self, state: AppState) -> AppState:
        return state

    def go_parent(self, state: AppState) -> AppState:
        return state


def _build_state(tmp_path: Path) -> AppState:
    a = FileEntry("a", tmp_path / "a", True)
    b = FileEntry("b.txt", tmp_path / "b.txt", False)
    return AppState(
        current_dir=tmp_path,
        parent_dir=tmp_path.parent,
        current_contents=[a, b],
        selected_index=0,
    )


def test_escape_exits(tmp_path: Path):
    state = _build_state(tmp_path)
    nav = FakeNavigator(state)
    renderer = FakeRenderer()

    keys = iter(["escape"])
    result = run_app(navigator=nav, renderer=renderer, key_reader=lambda: next(keys))

    assert result == 0
    assert len(renderer.rendered_states) == 1


def test_ctrl_c_clean_exit(tmp_path: Path):
    state = _build_state(tmp_path)
    nav = FakeNavigator(state)
    renderer = FakeRenderer()

    def raise_ctrl_c():
        raise KeyboardInterrupt()

    result = run_app(navigator=nav, renderer=renderer, key_reader=raise_ctrl_c)
    assert result == 0


def test_full_navigation_flow(tmp_path: Path):
    state = _build_state(tmp_path)
    nav = FakeNavigator(state)
    renderer = FakeRenderer()

    keys = iter(["down", "up", "left", "escape"])
    result = run_app(navigator=nav, renderer=renderer, key_reader=lambda: next(keys))

    assert result == 0
    assert nav.refresh_calls >= 1
    assert len(renderer.rendered_states) >= 1


def test_render_after_navigation(tmp_path: Path):
    state = _build_state(tmp_path)
    nav = FakeNavigator(state)
    renderer = FakeRenderer()

    keys = iter(["down", "escape"])
    run_app(navigator=nav, renderer=renderer, key_reader=lambda: next(keys))

    assert renderer.rendered_indexes[0] == 0
    assert renderer.rendered_indexes[1] == 1


def test_filesystem_change_detected(tmp_path: Path):
    state = _build_state(tmp_path)

    class ChangingNavigator(FakeNavigator):
        def refresh(self, state: AppState) -> AppState:
            self.refresh_calls += 1
            if self.refresh_calls == 1:
                state.error_message = "changed"
            return state

    nav = ChangingNavigator(state)
    renderer = FakeRenderer()

    keys = iter(["escape"])
    run_app(navigator=nav, renderer=renderer, key_reader=lambda: next(keys))

    assert renderer.rendered_states[0].error_message == "changed"
