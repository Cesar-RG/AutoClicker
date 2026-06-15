"""Configuracion de hotkeys globales para Windows.

En Windows, la libreria 'keyboard' permite registrar atajos de teclado
que funcionan en todo el sistema, incluso cuando la ventana de la
aplicacion no tiene el foco.

Los callbacks de keyboard se ejecutan en un hilo externo, por lo que
NO deben modificar la UI directamente. En su lugar, emiten signals de
Qt que se encolan en el hilo principal de forma segura.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("autoclicker")

# keyboard solo se importa si esta disponible (Windows)
import keyboard  # noqa: E402  # type: ignore[import-untyped]


def registrar_hotkeys_globales(
    senal_iniciar: Any,
    senal_detener: Any,
    senal_emergencia: Any,
) -> list[Any]:
    """Registra los atajos globales F1, F2 y Escape.

    Args:
        senal_iniciar: Signal de Qt que se emitira al presionar F1.
        senal_detener: Signal de Qt que se emitira al presionar F2.
        senal_emergencia: Signal de Qt que se emitira al presionar Escape.

    Returns:
        Lista de listeners registrados (para poder eliminarlos despues).
    """
    listeners: list[Any] = []
    try:
        listeners = [
            keyboard.add_hotkey("f1", senal_iniciar.emit),
            keyboard.add_hotkey("f2", senal_detener.emit),
            keyboard.add_hotkey("esc", senal_emergencia.emit),
        ]
        if all(listeners):
            logger.info("Hotkeys globales de Windows activados")
        else:
            logger.warning(
                "Algunos hotkeys globales no se registraron correctamente"
            )
    except Exception:
        logger.exception("No se pudieron registrar los hotkeys globales")
        return []
    return listeners


def eliminar_hotkeys_globales(listeners: list[Any]) -> None:
    """Elimina los listeners de hotkeys registrados."""
    for listener in listeners:
        if listener is None:
            continue
        try:
            keyboard.remove_hotkey(listener)
        except Exception:
            logger.warning("No se pudo eliminar un listener de teclado")
