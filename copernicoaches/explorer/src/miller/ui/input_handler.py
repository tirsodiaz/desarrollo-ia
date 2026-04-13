"""Captura de teclas multiplataforma."""

import sys


def read_key() -> str:
    """Lee una tecla y devuelve su identificador normalizado.

    Retorna: "up", "down", "left", "right", "escape", o "unknown".
    """
    if sys.platform == "win32":
        return _read_key_windows()
    else:
        return _read_key_unix()


def _read_key_windows() -> str:
    """Captura de teclas en Windows usando msvcrt."""
    import msvcrt

    ch = msvcrt.getwch()

    # Ctrl+C
    if ch == "\x03":
        raise KeyboardInterrupt

    # Escape
    if ch == "\x1b":
        return "escape"

    # Teclas especiales en Windows: prefijo \x00 o \xe0
    # getwch() bloquea hasta recibir el segundo byte del par de escape
    if ch in ("\x00", "\xe0"):
        ch2 = msvcrt.getwch()
        match ch2:
            case "H":
                return "up"
            case "P":
                return "down"
            case "K":
                return "left"
            case "M":
                return "right"
            case _:
                return "unknown"

    return "unknown"


def _read_key_unix() -> str:
    """Captura de teclas en Linux/macOS usando termios."""
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)

        # Ctrl+C
        if ch == "\x03":
            raise KeyboardInterrupt

        # Escape
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                match ch3:
                    case "A":
                        return "up"
                    case "B":
                        return "down"
                    case "C":
                        return "right"
                    case "D":
                        return "left"
            # Escape solo (sin secuencia ANSI completa)
            return "escape"

        return "unknown"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
