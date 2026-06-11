"""Tests para AutoClicker."""

from __future__ import annotations

import sys
import threading
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock de pyautogui ANTES de importar el módulo (evita dependencia de tkinter)
# ---------------------------------------------------------------------------
_mock_pyautogui = MagicMock()
_mock_pyautogui.FAILSAFE = True
_mock_pyautogui.position.return_value = MagicMock(x=100, y=100)
sys.modules["pyautogui"] = _mock_pyautogui

from autoclicker import ClickThread, SYSTEM, STYLESHEET  # noqa: E402

import pytest  # noqa: E402


class TestClickThread:
    """Pruebas del hilo de clics."""

    def test_initial_state(self) -> None:
        thread = ClickThread()
        assert thread.running is False
        assert thread.interval == 1.0

    def test_set_interval(self) -> None:
        thread = ClickThread()
        thread.set_interval(0.5)
        assert thread.interval == 0.5

    def test_running_property_thread_safety(self) -> None:
        """Verifica que running se puede leer/escribir desde múltiples hilos."""
        thread = ClickThread()
        errors: list[Exception] = []

        def writer() -> None:
            try:
                for _ in range(1000):
                    thread.running = True
                    thread.running = False
            except Exception as e:
                errors.append(e)

        def reader() -> None:
            try:
                for _ in range(1000):
                    _ = thread.running
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=reader),
            threading.Thread(target=writer),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Errores de concurrencia: {errors}"

    def test_run_stops_when_running_false(self, qtbot) -> None:  # noqa: ANN001
        """El hilo debe detenerse cuando running es False."""
        thread = ClickThread()
        thread.set_interval(0.01)
        thread.start()
        qtbot.wait(100)
        thread.running = False
        thread.wait(2000)
        assert not thread.isRunning()

    def test_run_emits_signal(self, qtbot) -> None:  # noqa: ANN001
        """Verifica que el hilo emite clicks_updated."""
        thread = ClickThread()
        thread.set_interval(0.01)
        signals_received: list[int] = []

        thread.clicks_updated.connect(lambda c: signals_received.append(c))
        with qtbot.wait_signal(thread.clicks_updated, timeout=1000):
            thread.start()

        thread.running = False
        thread.wait(2000)

        assert len(signals_received) > 0
        assert signals_received == sorted(signals_received)

    def test_exception_handling(self, qtbot) -> None:  # noqa: ANN001
        """Un error en pyautogui no debe crashear el hilo."""
        _mock_pyautogui.click.side_effect = RuntimeError("Fallo simulado")

        thread = ClickThread()
        thread.set_interval(0.01)
        thread.start()
        qtbot.wait(100)
        thread.wait(2000)

        assert not thread.isRunning()

        # Limpiar side_effect
        _mock_pyautogui.click.side_effect = None


class TestStylesheet:
    """Validación del stylesheet."""

    def test_stylesheet_is_string(self) -> None:
        assert isinstance(STYLESHEET, str)

    def test_stylesheet_contains_key_selectors(self) -> None:
        for selector in ("QMainWindow", "QPushButton", "QSpinBox"):
            assert selector in STYLESHEET, f"Falta selector {selector}"


class TestSystemDetection:
    """Verifica que la detección de SO funciona."""

    def test_system_is_string(self) -> None:
        assert isinstance(SYSTEM, str)
        assert len(SYSTEM) > 0
