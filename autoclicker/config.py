"""Deteccion del sistema operativo, constantes y configuracion de logging."""

from __future__ import annotations

import logging
import os
import platform

# -- Sistema operativo --------------------------------------------------------

SYSTEM: str = platform.system()  # "Windows", "Linux" o "Darwin" (macOS)
IS_WINDOWS: bool = SYSTEM == "Windows"
IS_LINUX: bool = SYSTEM == "Linux"
IS_MACOS: bool = SYSTEM == "Darwin"

# En Linux, Wayland bloquea pyautogui y keyboard (necesitan X11)
IS_WAYLAND: bool = (
    IS_LINUX and os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
)

# -- Hotkeys globales (solo disponibles en Windows) ---------------------------

KEYBOARD_AVAILABLE: bool = False
try:
    import keyboard  # noqa: F401

    KEYBOARD_AVAILABLE = True
except ImportError:
    pass

# En Windows con keyboard disponible se usan hotkeys globales.
# En Linux/macOS se usan hotkeys de ventana (solo funcionan con el foco puesto).
USE_GLOBAL_HOTKEYS: bool = IS_WINDOWS and KEYBOARD_AVAILABLE

# -- Logging ------------------------------------------------------------------

logger = logging.getLogger("autoclicker")
logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_handler)

# -- Tema visual de la aplicacion ---------------------------------------------

STYLESHEET: str = """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #2c3e50, stop:1 #34495e);
        color: white;
    }
    QLabel {
        color: white;
        padding: 5px;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #3498db, stop:1 #2980b9);
        border: none;
        border-radius: 10px;
        color: white;
        padding: 12px;
        font-weight: bold;
        font-size: 14px;
        min-height: 45px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #5dade2, stop:1 #3498db);
    }
    QPushButton:pressed {
        background: #2980b9;
    }
    QPushButton:disabled {
        background: #7f8c8d;
    }
    QSpinBox {
        background: #ecf0f1;
        border: 2px solid #bdc3c7;
        border-radius: 8px;
        padding: 8px;
        font-size: 14px;
        color: #2c3e50;
        min-height: 35px;
    }
"""
