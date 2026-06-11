"""AutoClicker Multiplataforma — PySide6 + pyautogui.

Hotkeys globales en Windows (vía ``keyboard``), de ventana en Linux/macOS.
"""

from __future__ import annotations

import logging
import os
import platform
import sys
import threading
import time
from typing import Any

import pyautogui
from PySide6.QtCore import QSettings, Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

try:
    import keyboard  # Solo Windows; en Linux requiere sudo

    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("autoclicker")
logger.setLevel(logging.DEBUG)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_handler)

# ---------------------------------------------------------------------------
# Detección de sistema operativo y entorno
# ---------------------------------------------------------------------------
SYSTEM: str = platform.system()
IS_WINDOWS: bool = SYSTEM == "Windows"
IS_LINUX: bool = SYSTEM == "Linux"
IS_MACOS: bool = SYSTEM == "Darwin"

IS_WAYLAND: bool = IS_LINUX and os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
if IS_WAYLAND:
    logger.warning(
        "Wayland detectado — pyautogui y keyboard requieren X11. "
        "Cierra la sesión y elige «GNOME on Xorg» o similar."
    )

pyautogui.FAILSAFE = True

USE_GLOBAL_HOTKEYS: bool = IS_WINDOWS and KEYBOARD_AVAILABLE
logger.info("SO: %s | Hotkeys: %s", SYSTEM, "GLOBALES" if USE_GLOBAL_HOTKEYS else "VENTANA")

# ---------------------------------------------------------------------------
# Constantes de estilo
# ---------------------------------------------------------------------------
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


# ===================================================================
# ClickThread
# ===================================================================
class ClickThread(QThread):
    """Hilo que ejecuta clics a intervalos regulares en la posición actual."""

    clicks_updated = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self._running = False
        self.interval: float = 1.0

    @property
    def running(self) -> bool:
        with self._lock:
            return self._running

    @running.setter
    def running(self, value: bool) -> None:
        with self._lock:
            self._running = value

    def set_interval(self, interval: float) -> None:
        self.interval = interval

    def run(self) -> None:
        self.running = True
        clicks = 0
        while self.running:
            try:
                current_pos = pyautogui.position()
                pyautogui.click(current_pos.x, current_pos.y)
                clicks += 1
                self.clicks_updated.emit(clicks)
                time.sleep(self.interval)
            except Exception:
                logger.exception("Error en el hilo de clics")
                break


# ===================================================================
# AutoclickerWindow
# ===================================================================
class AutoclickerWindow(QMainWindow):
    """Ventana principal del AutoClicker."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("🖱️ AutoClicker Multiplataforma")
        self.setFixedSize(500, 450)

        self.clicking: bool = False
        self.click_thread: ClickThread | None = None
        self.total_clicks: int = 0
        self.keyboard_listeners: list[Any] = []

        self.setStyleSheet(STYLESHEET)

        self._settings = QSettings("AutoClicker", "AutoClicker")

        self._init_ui()
        self._setup_input()
        self._restore_settings()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _init_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # SO detectado
        so_label = QLabel(f"🖥️ {SYSTEM}" + (" (Wayland ⚠️)" if IS_WAYLAND else ""))
        so_label.setStyleSheet("color: #e67e22;" if IS_WAYLAND else "color: #2ecc71; font-size: 14px;")
        so_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(so_label)

        # CPS
        cps_layout = QHBoxLayout()
        cps_label = QLabel("Clics/Segundo:")
        cps_label.setFont(QFont("Segoe UI", 12))
        cps_layout.addWidget(cps_label)

        self.cps_spin = QSpinBox()
        self.cps_spin.setRange(1, 20)
        self.cps_spin.setValue(2)
        self.cps_spin.setSuffix(" CPS")
        self.cps_spin.setFont(QFont("Segoe UI", 12))
        cps_layout.addWidget(self.cps_spin)
        cps_layout.addStretch()
        layout.addLayout(cps_layout)

        # Contador
        self.clicks_label = QLabel("Clics: 0")
        self.clicks_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.clicks_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.clicks_label)

        # Status
        self.status_label = QLabel("✅ Listo")
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Botones
        buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ INICIAR")
        self.start_btn.clicked.connect(self.start_clicking)
        buttons_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹ DETENER")
        self.stop_btn.clicked.connect(self.stop_clicking)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        layout.addLayout(buttons_layout)

        # Info hotkeys
        if USE_GLOBAL_HOTKEYS:
            hotkey_info = QLabel("🌐 F1=INICIAR  F2=DETENER  ESC=EMERGENCIA\n(Hotkeys GLOBALES)")
            hotkey_info.setStyleSheet("color: #2ecc71; font-size: 12px;")
        else:
            hotkey_info = QLabel("🪟 F1=INICIAR  F2=DETENER  ESC=EMERGENCIA\n(Clic en ventana primero)")
            hotkey_info.setStyleSheet("color: #f39c12; font-size: 12px;")
        hotkey_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(hotkey_info)

        # Failsafe
        failsafe_label = QLabel("⚠️ Esquina sup. izq. = FAILSAFE de emergencia")
        failsafe_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        failsafe_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(failsafe_label)

    # ------------------------------------------------------------------
    # Configuración de entrada
    # ------------------------------------------------------------------
    def _setup_input(self) -> None:
        if USE_GLOBAL_HOTKEYS:
            self._setup_global_hotkeys()
        else:
            self.setFocusPolicy(Qt.StrongFocus)
            logger.info("Hotkeys de ventana activados (Linux/macOS)")

    def _setup_global_hotkeys(self) -> None:
        try:
            self.keyboard_listeners = [
                keyboard.add_hotkey("f1", self._on_hotkey_start),
                keyboard.add_hotkey("f2", self._on_hotkey_stop),
                keyboard.add_hotkey("esc", self.emergency_stop),
            ]
            if all(self.keyboard_listeners):
                logger.info("Hotkeys GLOBALES Windows activados")
            else:
                logger.warning("Algunos hotkeys globales no se registraron correctamente")
        except Exception:
            logger.exception("No se pudieron registrar hotkeys globales")
            self.keyboard_listeners = []

    def _on_hotkey_start(self) -> None:
        if not self.clicking:
            self.start_clicking()

    def _on_hotkey_stop(self) -> None:
        self.stop_clicking()

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def _restore_settings(self) -> None:
        cps = self._settings.value("cps", 2, type=int)
        self.cps_spin.setValue(cps)
        logger.debug("Configuración restaurada: CPS=%d", cps)

    def _save_settings(self) -> None:
        self._settings.setValue("cps", self.cps_spin.value())
        self._settings.sync()

    # ------------------------------------------------------------------
    # Eventos de teclado (ventana)
    # ------------------------------------------------------------------
    def keyPressEvent(self, event: Any) -> None:  # noqa: N802
        if USE_GLOBAL_HOTKEYS:
            super().keyPressEvent(event)
            return

        key = event.key()
        if key == Qt.Key_F1 and not self.clicking:
            self.start_clicking()
        elif key == Qt.Key_F2:
            self.stop_clicking()
        elif key == Qt.Key_Escape:
            self.emergency_stop()

        super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Control de clics
    # ------------------------------------------------------------------
    def start_clicking(self) -> None:
        if self.clicking:
            return

        self._save_settings()

        # Solo en Windows (hotkeys globales): quitar foco para no interferir
        if USE_GLOBAL_HOTKEYS:
            self.setFocusPolicy(Qt.NoFocus)
            QApplication.processEvents()

        cps = self.cps_spin.value()
        self.click_thread = ClickThread()
        self.click_thread.set_interval(1.0 / cps)
        self.click_thread.clicks_updated.connect(self._update_clicks)

        self.clicking = True
        self.total_clicks = 0
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("🔄 Cliqueando...")
        self.click_thread.start()
        logger.info("Clics iniciados (CPS=%d)", cps)

    def stop_clicking(self) -> None:
        if self.click_thread is not None:
            self.click_thread.running = False
            self.click_thread.quit()
            self.click_thread.wait(1000)
        self.clicking = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("⏸️ Detenido")

        if USE_GLOBAL_HOTKEYS:
            self.setFocusPolicy(Qt.StrongFocus)
        logger.info("Clics detenidos (total=%d)", self.total_clicks)

    def emergency_stop(self) -> None:
        self.stop_clicking()
        self.status_label.setText("🛑 EMERGENCIA")
        logger.warning("Parada de emergencia")

    def _update_clicks(self, clicks: int) -> None:
        self.total_clicks = clicks
        self.clicks_label.setText(f"Clics: {clicks:,}")

    # ------------------------------------------------------------------
    # Cierre
    # ------------------------------------------------------------------
    def closeEvent(self, event: Any) -> None:  # noqa: N802
        self._save_settings()
        for listener in self.keyboard_listeners:
            try:
                keyboard.remove_hotkey(listener)
            except Exception:
                logger.warning("No se pudo eliminar un listener de teclado")
        self.stop_clicking()
        event.accept()


# ===================================================================
# Punto de entrada
# ===================================================================
def main() -> None:
    app = QApplication(sys.argv)
    window = AutoclickerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
