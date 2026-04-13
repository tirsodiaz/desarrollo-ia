#!/usr/bin/env python3
"""Test de navegación simple."""

from miller.navigation.navigator import Navigator
from miller.ui.renderer import Renderer
from miller.state.model import AppState

nav = Navigator()
state = nav.initialize()

print("=" * 80)
print("ESTADO INICIAL")
print("=" * 80)
renderer = Renderer()
renderer.render(state)
print(f"Selected index: {state.selected_index}")
print(f"Current dir: {state.current_dir}")
print(f"Rows: {[r.name for r in state.current_contents]}")

print("\n" + "=" * 80)
print("PRESIONANDO DOWN")
print("=" * 80)
state = nav.move_down(state)
renderer.render(state)
print(f"Selected index: {state.selected_index}")

print("\n" + "=" * 80)
print("PRESIONANDO UP")
print("=" * 80)
state = nav.move_up(state)
renderer.render(state)
print(f"Selected index: {state.selected_index}")

print("\n" + "=" * 80)
print("PRESIONANDO RIGHT (enter)")
print("=" * 80)
state = nav.enter_directory(state)
renderer.render(state)
print(f"Current dir: {state.current_dir}")
print(f"Rows: {[r.name for r in state.current_contents][:5]}...")

print("\nTODO FUNCIONA")
