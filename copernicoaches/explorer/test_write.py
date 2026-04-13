#!/usr/bin/env python3
"""Verificar que podemos escribir archivos."""

import os

path = os.path.dirname(os.path.abspath(__file__))
test_file = os.path.join(path, "test_write.txt")

try:
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("Test de escritura OK\n")
    print(f"✓ Archivo creado en: {test_file}")
except Exception as e:
    print(f"ERROR escribiendo: {e}")
