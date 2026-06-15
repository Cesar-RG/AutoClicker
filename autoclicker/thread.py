"""Hilo que ejecuta los clics automaticos a intervalos regulares."""

from __future__ import annotations

import time

import pyautogui
from PySide6.QtCore import QThread, Signal

# El failsafe de pyautogui detiene todo si el mouse va a la esquina superior
# izquierda de la pantalla. Se activa en el modulo principal.
pyautogui.FAILSAFE = True


class ClickThread(QThread):
    """Ejecuta clics en bucle mientras no se solicite su interrupcion.

    Usa requestInterruption() para detenerlo de forma segura desde
    cualquier hilo, sin necesidad de flags propias.
    """

    # Senal que emite el contador de clics acumulado
    clicks_updated = Signal(int)

    # Intervalo entre clics, en segundos. Se calcula como 1 / CPS.
    interval: float

    def __init__(self) -> None:
        super().__init__()
        self.interval = 1.0

    def set_interval(self, interval: float) -> None:
        """Actualiza el intervalo entre clics."""
        self.interval = interval

    def run(self) -> None:
        """Bucle principal del hilo. Hace clic en la posicion actual del mouse
        y espera el intervalo configurado. Se detiene cuando se llama a
        requestInterruption()."""
        clicks = 0
        while not self.isInterruptionRequested():
            try:
                posicion_actual = pyautogui.position()
                pyautogui.click(posicion_actual.x, posicion_actual.y)
                clicks += 1
                self.clicks_updated.emit(clicks)
                time.sleep(self.interval)
            except Exception:
                import logging

                logging.getLogger("autoclicker").exception(
                    "Error en el hilo de clics"
                )
                break
