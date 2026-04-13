#!/usr/bin/env python3
"""Debug - Captura TODOS los bytes sin interpretar."""

import sys
import os

if sys.platform != "win32":
    print("Solo Windows")
    sys.exit(1)

path = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(path, "debug_output.txt")

print("Presiona 10 flechas RÁPIDAMENTE sin esperar. Ctrl+C para salir.")
print(f"Guardando en: {log_file}\n")

import msvcrt
import time

with open(log_file, "w") as f:
    f.write("=== CAPTURA BRUTA - TODO LO QUE LLEGA ===\n\n")

try:
    # Acumular todos los bytes que lleguen
    bytes_captured = []
    start = time.time()
    
    while time.time() - start < 15:  # Esperar 15 segundos
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            ts = time.time() - start
            bytes_captured.append((ts, ch))
            
            # Mostrar en pantalla
            print(f"[{ts:.2f}s] {repr(ch)} (ord {ord(ch)})")
            
            # Guardar
            with open(log_file, "a") as f:
                f.write(f"[{ts:.2f}s] {repr(ch)} (ord {ord(ch)})\n")
        
        time.sleep(0.001)
    
    if not bytes_captured:
        print("ERROR: No se capturaron teclas")
        with open(log_file, "a") as f:
            f.write("ERROR: No se capturaron teclas en 15 segundos\n")

except KeyboardInterrupt:
    with open(log_file, "a") as f:
        f.write("\n[Interrumpido por usuario]\n")
    print(f"\nInterrumpido")

print(f"\nRevisa {log_file}")
