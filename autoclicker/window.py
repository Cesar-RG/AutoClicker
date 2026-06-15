"""Ventana principal del AutoClicker."""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from autoclicker.config import (
    IS_WAYLAND,
    STYLESHEET,
    SYSTEM,
    USE_GLOBAL_HOTKEYS,
)
from autoclicker.thread import ClickThread

logger = logging.getLogger("autoclicker")


class AutoclickerWindow(QMainWindow):
    """Interfaz grafica principal del autoclicker.

    Permite configurar la frecuencia de clics (CPS), iniciar y detener
    el autoclicker, y muestra un contador en tiempo real.

    Las hotkeys funcionan de forma distinta segun la plataforma:
    - Windows: atajos globales del sistema (funcionan sin foco).
    - Linux/macOS: atajos de ventana (requieren que la ventana tenga el foco).
    """

    # Signals para que los callbacks de hotkeys externos (Windows) puedan
    # comunicarse con el hilo principal de Qt de forma segura.
    hotkey_start = Signal()
    hotkey_stop = Signal()
    hotkey_emergency = Signal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AutoClicker Multiplataforma")
        self.setFixedSize(500, 450)

        # Estado interno
        self.clicking: bool = False
        self.click_thread: ClickThread | None = None
        self.total_clicks: int = 0
        self.keyboard_listeners: list[Any] = []

        self.setStyleSheet(STYLESHEET)

        # Persistencia de la configuracion entre sesiones
        self._settings = QSettings("AutoClicker", "AutoClicker")

        # Conectar signals de hotkeys a los metodos correspondientes
        self.hotkey_start.connect(self.start_clicking)
        self.hotkey_stop.connect(self.stop_clicking)
        self.hotkey_emergency.connect(self.emergency_stop)

        self._init_ui()
        self._configurar_hotkeys()
        self._restore_settings()

    # -- Construccion de la interfaz ------------------------------------------

    def _init_ui(self) -> None:
        """Construye todos los widgets y layouts de la ventana."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Etiqueta con el sistema operativo detectado
        texto_so = SYSTEM
        if IS_WAYLAND:
            texto_so += " (Wayland: incompatible)"
        so_label = QLabel(texto_so)
        so_label.setStyleSheet(
            "color: #e67e22;" if IS_WAYLAND else "color: #2ecc71; font-size: 14px;"
        )
        so_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(so_label)

        # Selector de clics por segundo (CPS)
        cps_layout = QHBoxLayout()
        cps_label = QLabel("Clics por segundo:")
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

        # Contador de clics en tiempo real
        self.clicks_label = QLabel("Clics: 0")
        self.clicks_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.clicks_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.clicks_label)

        # Estado actual (listo, cliqueando, detenido, emergencia)
        self.status_label = QLabel("Listo")
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Botones de control
        buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton("Iniciar")
        self.start_btn.clicked.connect(self.start_clicking)
        buttons_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Detener")
        self.stop_btn.clicked.connect(self.stop_clicking)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        layout.addLayout(buttons_layout)

        # Informacion sobre las hotkeys disponibles
        if USE_GLOBAL_HOTKEYS:
            hotkey_info = QLabel(
                "F1 = Iniciar   F2 = Detener   Esc = Emergencia\n"
                "(Hotkeys globales: funcionan sin foco en la ventana)"
            )
            hotkey_info.setStyleSheet("color: #2ecc71; font-size: 12px;")
        else:
            hotkey_info = QLabel(
                "F1 = Iniciar   F2 = Detener   Esc = Emergencia\n"
                "(Hotkeys de ventana: haz clic aqui antes de usarlas)"
            )
            hotkey_info.setStyleSheet("color: #f39c12; font-size: 12px;")
        hotkey_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(hotkey_info)

        # Aviso de failsafe de pyautogui
        failsafe_label = QLabel(
            "Mueve el mouse a la esquina superior izquierda\n"
            "para detener todo instantaneamente (failsafe)"
        )
        failsafe_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        failsafe_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(failsafe_label)

    # -- Configuracion de hotkeys segun plataforma ----------------------------

    def _configurar_hotkeys(self) -> None:
        """Activa el sistema de hotkeys adecuado para esta plataforma."""
        if USE_GLOBAL_HOTKEYS:
            from autoclicker.hotkeys_windows import registrar_hotkeys_globales

            self.keyboard_listeners = registrar_hotkeys_globales(
                self.hotkey_start,
                self.hotkey_stop,
                self.hotkey_emergency,
            )
        else:
            from autoclicker.hotkeys_unix import activar_hotkeys_ventana

            activar_hotkeys_ventana()
            # La ventana necesita foco para recibir eventos de teclado
            self.setFocusPolicy(Qt.StrongFocus)

    # -- Persistencia de configuracion ----------------------------------------

    def _restore_settings(self) -> None:
        """Carga el CPS guardado de la sesion anterior."""
        cps = self._settings.value("cps", 2, type=int)
        self.cps_spin.setValue(cps)
        logger.debug("Configuracion restaurada: CPS=%d", cps)

    def _save_settings(self) -> None:
        """Guarda el CPS actual para la proxima sesion."""
        self._settings.setValue("cps", self.cps_spin.value())
        self._settings.sync()

    # -- Eventos de teclado (solo en Linux/macOS) -----------------------------

    def keyPressEvent(self, event: Any) -> None:  # noqa: N802
        """Maneja F1, F2 y Escape cuando las hotkeys son de ventana.

        En Windows este metodo no procesa las hotkeys porque se manejan
        globalmente a traves de signals.
        """
        if USE_GLOBAL_HOTKEYS:
            # En Windows las hotkeys las gestiona el sistema
            super().keyPressEvent(event)
            return

        key = event.key()
        if key == Qt.Key_F1 and not self.clicking:
            self.start_clicking()
        elif key == Qt.Key_F2:
            self.stop_clicking()
        elif key == Qt.Key_Escape:
            self.emergency_stop()
        else:
            super().keyPressEvent(event)

    # -- Control del autoclicker ----------------------------------------------

    def start_clicking(self) -> None:
        """Inicia el hilo de clics con la frecuencia configurada."""
        if self.clicking:
            return

        self._save_settings()

        # En Windows (hotkeys globales): quitar el foco para no interferir
        # con la aplicacion donde se quiere hacer clic.
        if USE_GLOBAL_HOTKEYS:
            self.setFocusPolicy(Qt.NoFocus)

        cps = self.cps_spin.value()
        self.click_thread = ClickThread()
        self.click_thread.set_interval(1.0 / cps)
        self.click_thread.clicks_updated.connect(self._actualizar_contador)

        self.clicking = True
        self.total_clicks = 0
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Cliqueando...")
        self.click_thread.start()
        logger.info("Clics iniciados (CPS=%d)", cps)

    def stop_clicking(self) -> None:
        """Detiene el hilo de clics de forma segura."""
        if self.click_thread is not None:
            self.click_thread.requestInterruption()
            self.click_thread.wait(2000)
        self.clicking = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Detenido")

        if USE_GLOBAL_HOTKEYS:
            # Recuperar el foco en la ventana
            self.setFocusPolicy(Qt.StrongFocus)
        logger.info("Clics detenidos (total=%d)", self.total_clicks)

    def emergency_stop(self) -> None:
        """Parada de emergencia. Igual que detener pero con aviso visual."""
        self.stop_clicking()
        self.status_label.setText("Emergencia")
        logger.warning("Parada de emergencia")

    def _actualizar_contador(self, clicks: int) -> None:
        """Actualiza el contador de clics en la interfaz."""
        self.total_clicks = clicks
        self.clicks_label.setText(f"Clics: {clicks:,}")

    # -- Cierre de la ventana -------------------------------------------------

    def closeEvent(self, event: Any) -> None:  # noqa: N802
        """Limpia los listeners de teclado y detiene el hilo al cerrar."""
        self._save_settings()
        if self.keyboard_listeners:
            try:
                from autoclicker.hotkeys_windows import eliminar_hotkeys_globales

                eliminar_hotkeys_globales(self.keyboard_listeners)
            except ImportError:
                pass
        self.stop_clicking()
        event.accept()
