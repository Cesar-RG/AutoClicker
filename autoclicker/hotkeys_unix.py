"""Configuracion de hotkeys de ventana para Linux y macOS.

En Linux y macOS no se usan hotkeys globales porque la libreria
'keyboard' requiere permisos de root en Linux y no esta disponible
en macOS.

En su lugar, la ventana principal captura los eventos de teclado
cuando tiene el foco (F1 = iniciar, F2 = detener, Esc = emergencia).
"""

from __future__ import annotations

import logging

logger = logging.getLogger("autoclicker")


def activar_hotkeys_ventana() -> None:
    """Indica que se usaran hotkeys de ventana (por defecto en Linux/macOS).

    La ventana debe tener el foco para que funcionen. El usuario debe
    hacer clic en la ventana antes de usar F1, F2 o Escape.
    """
    logger.info("Hotkeys de ventana activados (Linux/macOS)")
