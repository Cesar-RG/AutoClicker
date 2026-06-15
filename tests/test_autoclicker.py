"""Tests para AutoClicker."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock de pyautogui ANTES de importar el módulo (evita dependencia de tkinter)
# ---------------------------------------------------------------------------
_mock_pyautogui = MagicMock()
_mock_pyautogui.FAILSAFE = True
_mock_pyautogui.position.return_value = MagicMock(x=100, y=100)
sys.modules["pyautogui"] = _mock_pyautogui

import pytest  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent  # noqa: E402

from autoclicker.config import STYLESHEET, SYSTEM, USE_GLOBAL_HOTKEYS  # noqa: E402
from autoclicker.thread import ClickThread  # noqa: E402
from autoclicker.window import AutoclickerWindow  # noqa: E402


class TestClickThread:
    """Pruebas del hilo de clics."""

    def test_initial_state(self) -> None:
        thread = ClickThread()
        assert thread.isInterruptionRequested() is False
        assert thread.interval == 1.0

    def test_set_interval(self) -> None:
        thread = ClickThread()
        thread.set_interval(0.5)
        assert thread.interval == 0.5

    def test_run_stops_on_interruption(self, qtbot) -> None:  # noqa: ANN001
        """El hilo debe detenerse al llamar requestInterruption."""
        thread = ClickThread()
        thread.set_interval(0.01)
        thread.start()
        qtbot.wait(100)
        thread.requestInterruption()
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

        thread.requestInterruption()
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


class TestAutoclickerWindow:
    """Pruebas de la ventana principal."""

    def test_initial_state(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        assert window.clicking is False
        assert window.start_btn.isEnabled()
        assert not window.stop_btn.isEnabled()
        assert window.status_label.text() == "Listo"

    def test_start_clicking(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.cps_spin.setValue(2)
        window.start_clicking()

        assert window.clicking is True
        assert not window.start_btn.isEnabled()
        assert window.stop_btn.isEnabled()
        assert window.click_thread is not None
        assert window.click_thread.interval == 0.5  # 1 / 2 CPS

        window.stop_clicking()

    def test_start_clicking_idempotent(self, qtbot) -> None:  # noqa: ANN001
        """start_clicking no debe hacer nada si ya esta cliqueando."""
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.start_clicking()
        first_thread = window.click_thread
        window.start_clicking()

        assert window.click_thread is first_thread

        window.stop_clicking()

    def test_stop_clicking(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.start_clicking()
        window.stop_clicking()

        assert window.clicking is False
        assert window.start_btn.isEnabled()
        assert not window.stop_btn.isEnabled()
        assert not window.click_thread.isRunning()

    def test_emergency_stop(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.start_clicking()
        window.emergency_stop()

        assert window.clicking is False
        assert window.status_label.text() == "Emergencia"

    def test_cps_changes_interval(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.cps_spin.setValue(10)
        window.start_clicking()

        assert window.click_thread.interval == 0.1  # 1 / 10 CPS

        window.stop_clicking()

    def test_update_clicks(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window._actualizar_contador(42)
        assert window.clicks_label.text() == "Clics: 42"
        assert window.total_clicks == 42

    @pytest.mark.skipif(
        USE_GLOBAL_HOTKEYS,
        reason="keyPressEvent no procesa hotkeys en Windows (usa signals globales)",
    )
    def test_keypress_f1_starts(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_F1, Qt.NoModifier)
        window.keyPressEvent(event)

        assert window.clicking is True

        window.stop_clicking()

    @pytest.mark.skipif(
        USE_GLOBAL_HOTKEYS,
        reason="keyPressEvent no procesa hotkeys en Windows (usa signals globales)",
    )
    def test_keypress_f2_stops(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.start_clicking()

        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_F2, Qt.NoModifier)
        window.keyPressEvent(event)

        assert window.clicking is False

    @pytest.mark.skipif(
        USE_GLOBAL_HOTKEYS,
        reason="keyPressEvent no procesa hotkeys en Windows (usa signals globales)",
    )
    def test_keypress_escape_emergency(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.start_clicking()

        event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier)
        window.keyPressEvent(event)

        assert window.clicking is False
        assert window.status_label.text() == "Emergencia"

    def test_hotkey_signals_connected(self, qtbot) -> None:  # noqa: ANN001
        """Verifica que las signals de hotkey disparan los metodos."""
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.hotkey_start.emit()
        assert window.clicking is True

        window.hotkey_stop.emit()
        assert window.clicking is False

    def test_settings_persistence(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.cps_spin.setValue(15)
        window._save_settings()

        cps = window._settings.value("cps", type=int)
        assert cps == 15

    def test_close_event_cleans_up(self, qtbot) -> None:  # noqa: ANN001
        window = AutoclickerWindow()
        qtbot.addWidget(window)

        window.start_clicking()

        event = MagicMock()
        window.closeEvent(event)

        assert window.clicking is False
        event.accept.assert_called_once()
