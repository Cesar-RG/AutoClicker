"""AutoClicker Multiplataforma — PySide6 + pyautogui.

Hotkeys globales en Windows, de ventana en Linux/macOS.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from autoclicker.config import IS_WAYLAND, SYSTEM, USE_GLOBAL_HOTKEYS, logger
from autoclicker.window import AutoclickerWindow


def main() -> None:
    """Punto de entrada principal de la aplicacion."""
    # Aviso temprano si el entorno no es compatible
    if IS_WAYLAND:
        logger.warning(
            "Wayland detectado: pyautogui y keyboard requieren X11. "
            "Cierra la sesion y elige 'GNOME on Xorg' o similar."
        )

    logger.info(
        "SO: %s | Hotkeys: %s",
        SYSTEM,
        "GLOBALES" if USE_GLOBAL_HOTKEYS else "VENTANA",
    )

    app = QApplication(sys.argv)
    window = AutoclickerWindow()
    window.show()
    sys.exit(app.exec())
