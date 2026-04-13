#!/usr/bin/env python3
"""Verificar que el encabezado muestra la ruta del elemento seleccionado."""

from pathlib import Path
from miller.state.model import AppState, FileEntry
from miller.ui.renderer import render

# Usar el directorio raíz Windows como punto de partida
root = Path("C:\\")
contents = list(root.iterdir())[:10]  # Primeros 10 items

entries = [
    FileEntry(name=p.name, path=p, is_dir=p.is_dir())
    for p in contents
]

print("=" * 80)
print("TEST 1: Header with index 0 (first item selected)")
print("=" * 80)

state = AppState(
    current_dir=root,
    parent_dir=None,
    current_contents=entries,
    selected_index=0,
)

render(state, terminal_size=(80, 18))
print(f"\nENCUADRE → Selected: {entries[0].name}")
print(f"Expected header: Ruta: {entries[0].path}")

print("\n" + "=" * 80)
print("TEST 2: Header with index 5 (sixth item selected)")
print("=" * 80)

state.selected_index = 5
render(state, terminal_size=(80, 18))
print(f"\nENCUADRE → Selected: {entries[5].name}")
print(f"Expected header: Ruta: {entries[5].path}")

print("\n" + "=" * 80)
print("TEST 3: Header with index 9 (last item selected)")
print("=" * 80)

state.selected_index = 9
render(state, terminal_size=(80, 18))
print(f"\nENCUADRE → Selected: {entries[9].name}")
print(f"Expected header: Ruta: {entries[9].path}")

print("\n" + "=" * 80)
print("✓ All tests completed. Header should change as you move selection.")
print("=" * 80)
