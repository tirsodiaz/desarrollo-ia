#!/usr/bin/env python3
"""Verificar que el encabezado permanece visible al bajar con arrow down."""

from pathlib import Path
from miller.state.model import AppState, FileEntry
from miller.ui.renderer import render

# Crear carpeta de prueba con muchos items
test_path = Path("C:\\Windows\\System32")
# Listar archivos de System32 (hay muchos)
all_items = list(test_path.iterdir())[:50]

entries = [
    FileEntry(name=p.name, path=p, is_dir=p.is_dir())
    for p in all_items
]

print("=" * 80)
print("NAVEGACIÓN SIMULADA: Bajando desde índice 0 hasta 15")
print("=" * 80)
print("Verifica que el header 'Ruta: ...' esté SIEMPRE VISIBLE arriba")
print("=" * 80)

for i in [0, 5, 10, 15]:
    print(f"\n>>> Movimiento DOWN: index = {i} <<<\n")
    
    state = AppState(
        current_dir=test_path,
        parent_dir=test_path.parent,
        current_contents=entries,
        selected_index=i,
    )
    
    render(state, terminal_size=(100, 20))
    print(f"Seleccionado: {entries[i].name}")
    print(f"Esperado que veas: Ruta: {entries[i].path}")
    print("\n" + "-" * 80)

print("\n✓ Test completado. El header debería ser visible en TODAS las pantallas.")
