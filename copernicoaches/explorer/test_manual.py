#!/usr/bin/env python3
"""Test manual para simular la app con pasos controlados."""

from miller.navigation.navigator import Navigator
from miller.ui.renderer import Renderer

nav = Navigator()
renderer = Renderer()
state = nav.initialize()

print("=== ESTADO 0: DRIVES ===")
renderer.render(state)
print(f"Selected: {state.selected_index}, At drives: {state.is_at_drives}")

print("\n=== SIMULANDO ENTER (RIGHT) ===")
state = nav.enter_directory(state)
print(f"After enter:")
print(f"  Current dir: {state.current_dir}")
print(f"  Content count: {len(state.current_contents)}")
print(f"  Selected: {state.selected_index}")
print(f"  At drives: {state.is_at_drives}")

print("\n=== RENDERING C: ===")
renderer.render(state)
print("=== RENDERED ===")

print("\n=== SIMULANDO MOVE DOWN ===")
state = nav.move_down(state)
print(f"Selected now: {state.selected_index}")
renderer.render(state)
print("=== RENDERED ===")

print("\nSUCCESS")
