"""Punto de entrada e integración de Miller Columns."""

from collections.abc import Callable

from miller.navigation.navigator import Navigator
from miller.state.model import AppState
from miller.ui.input_handler import read_key
from miller.ui.renderer import Renderer


def run_app(
    navigator: Navigator | None = None,
    renderer: Renderer | None = None,
    key_reader: Callable[[], str] | None = None,
) -> int:
    """Ejecuta el bucle principal de la aplicación."""
    active_navigator = navigator or Navigator()
    active_renderer = renderer or Renderer()
    active_key_reader = key_reader or read_key

    state: AppState = active_navigator.initialize()

    def _run_loop(initial_state: AppState) -> int:
        current_state = initial_state
        while True:
            current_state = active_navigator.refresh(current_state)
            try:
                active_renderer.render(current_state)
            except Exception as exc:
                import sys
                print(f"\nRender error: {exc}", file=sys.stderr)

            key = active_key_reader()
            match key:
                case "up":
                    current_state = active_navigator.move_up(current_state)
                case "down":
                    current_state = active_navigator.move_down(current_state)
                case "right":
                    current_state = active_navigator.enter_directory(current_state)
                case "left":
                    current_state = active_navigator.go_parent(current_state)
                case "escape":
                    return 0
                case _:
                    continue

    try:
        return _run_loop(state)
    except KeyboardInterrupt:
        return 0
    finally:
        pass


def main() -> int:
    """Punto de entrada de la aplicación Miller Columns."""
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
