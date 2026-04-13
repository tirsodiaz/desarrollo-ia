"""Lógica de navegación — gestiona eventos y actualiza el estado."""

import os
import sys
from pathlib import Path

from miller.filesystem.reader import (
    detect_changes,
    get_parent,
    list_directory,
    list_drives,
)
from miller.state.model import AppState


class Navigator:
    """Gestiona la navegación y actualiza el estado de la aplicación."""

    def initialize(self) -> AppState:
        """Crea el estado inicial mostrando las unidades de disco."""
        drives = list_drives()
        return AppState(
            current_dir=Path("/drives"),  # Ruta virtual para el nivel de unidades
            parent_dir=None,
            current_contents=drives,
            selected_index=0 if drives else -1,
            is_at_drives=True,
        )

    def move_up(self, state: AppState) -> AppState:
        """Mueve la selección al elemento anterior."""
        state.error_message = None
        if state.selected_index > 0:
            state.selected_index -= 1
        return state

    def move_down(self, state: AppState) -> AppState:
        """Mueve la selección al elemento siguiente."""
        state.error_message = None
        if 0 <= state.selected_index < len(state.current_contents) - 1:
            state.selected_index += 1
        return state

    def enter_directory(self, state: AppState) -> AppState:
        """Entra en el directorio seleccionado (flecha derecha)."""
        if state.selected_index < 0 or state.selected_index >= len(state.current_contents):
            return state

        selected = state.current_contents[state.selected_index]

        # No hacer nada si es un archivo (a menos que estemos en unidades)
        if not selected.is_dir:
            return state

        # Si estamos en el nivel de unidades, entrar en la unidad seleccionada
        if state.is_at_drives:
            try:
                new_contents = list_directory(selected.path)
            except (PermissionError, OSError) as e:
                state.error_message = f"Error: {e}"
                return state

            state.parent_dir = None  # No hay "padre" que no sea unidades
            state.current_dir = selected.path
            state.current_contents = new_contents
            state.selected_index = 0 if new_contents else -1
            state.is_at_drives = False
            state.error_message = None
            return state

        # Caso normal: entrar en un subdirectorio
        try:
            new_contents = list_directory(selected.path)
        except (PermissionError, OSError) as e:
            state.error_message = f"Error: {e}"
            return state

        # Si list_directory devuelve vacío, verificar si es por error de acceso
        # probando iterdir directamente
        if not new_contents:
            try:
                list(selected.path.iterdir())
            except PermissionError:
                state.error_message = "Error: acceso denegado"
                return state
            except OSError as e:
                state.error_message = f"Error: {e}"
                return state

        state.parent_dir = state.current_dir
        state.current_dir = selected.path
        state.current_contents = new_contents
        state.selected_index = 0 if new_contents else -1
        state.error_message = None
        return state

    def go_parent(self, state: AppState) -> AppState:
        """Retorna al directorio padre o al nivel de unidades (flecha izquierda)."""
        # Si estamos en el nivel de unidades, no hacer nada
        if state.is_at_drives:
            return state

        # Si no hay padre, estamos en la raíz de una unidad
        # Volver al nivel de unidades
        if state.parent_dir is None:
            drives = list_drives()
            # Buscar la unidad actual en la lista de unidades
            # Usar .drive para obtener "C:" de Path("C:\\")
            current_drive = state.current_dir.drive if state.current_dir.drive else state.current_dir.name
            selected_index = 0
            for i, drive in enumerate(drives):
                if drive.name == current_drive:
                    selected_index = i
                    break

            state.current_dir = Path("/drives")
            state.parent_dir = None
            state.current_contents = drives
            state.selected_index = selected_index if drives else -1
            state.is_at_drives = True
            state.error_message = None
            return state

        # Caso normal: volver al padre
        old_dir_name = state.current_dir.name
        new_dir = state.parent_dir
        new_parent = get_parent(new_dir)
        new_contents = list_directory(new_dir)

        # Buscar el índice del directorio desde el que se regresó
        selected_index = 0
        for i, entry in enumerate(new_contents):
            if entry.name == old_dir_name and entry.is_dir:
                selected_index = i
                break

        state.current_dir = new_dir
        state.parent_dir = new_parent
        state.current_contents = new_contents
        state.selected_index = selected_index if new_contents else -1
        state.error_message = None
        return state

    def refresh(self, state: AppState) -> AppState:
        """Refresca el estado detectando cambios en el filesystem."""
        # Si estamos en el nivel de unidades, refrescar la lista de unidades
        if state.is_at_drives:
            new_contents = list_drives()
            # Mantener la selección si es posible
            old_name = None
            if 0 <= state.selected_index < len(state.current_contents):
                old_name = state.current_contents[state.selected_index].name
            
            state.current_contents = new_contents
            if new_contents:
                selected_index = 0
                if old_name:
                    for i, entry in enumerate(new_contents):
                        if entry.name == old_name:
                            selected_index = i
                            break
                state.selected_index = selected_index
            else:
                state.selected_index = -1
            return state

        # Verificar si el directorio actual aún existe
        if not state.current_dir.exists():
            if state.parent_dir is not None:
                return self.go_parent(state)
            return state

        if not detect_changes(state.current_dir, state.current_contents):
            return state

        new_contents = list_directory(state.current_dir)

        # Intentar mantener la selección en el mismo elemento
        old_selected_name = None
        if 0 <= state.selected_index < len(state.current_contents):
            old_selected_name = state.current_contents[state.selected_index].name

        state.current_contents = new_contents

        if not new_contents:
            state.selected_index = -1
        elif old_selected_name:
            # Buscar el elemento previamente seleccionado
            found = False
            for i, entry in enumerate(new_contents):
                if entry.name == old_selected_name:
                    state.selected_index = i
                    found = True
                    break
            if not found:
                state.selected_index = min(state.selected_index, len(new_contents) - 1)
        else:
            state.selected_index = 0

        return state
