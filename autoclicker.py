"""
 AUTOCICKER MULTIPLATAFORMA
PySide6 + Auto-detect Windows/Linux/macOS
Hotkeys GLOBALES en Windows, VENTANA en Linux
"""

import sys
import platform
import pyautogui
import time
try:
    import keyboard  # Solo para Windows
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                              QWidget, QLabel, QSpinBox, QPushButton)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont

# Auto-detect SO
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"
IS_MACOS = SYSTEM == "Darwin"

pyautogui.FAILSAFE = True

print(f"SO: {SYSTEM}")
print(f" Hotkeys: {'GLOBALES' if IS_WINDOWS and KEYBOARD_AVAILABLE else 'VENTANA'}")

class ClickThread(QThread):
    clicks_updated = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.interval = 1.0
    
    def set_interval(self, interval):
        self.interval = interval
    
    def run(self):
        self.running = True
        clicks = 0
        while self.running:
            try:
                # 🎯 Tomar posición ACTUAL del mouse
                current_pos = pyautogui.position()
                # ✅ CLIC EXACTO donde está el mouse (NO mueve)
                pyautogui.click(current_pos.x, current_pos.y)
                clicks += 1
                self.clicks_updated.emit(clicks)
                time.sleep(self.interval)
            except:
                break

class AutoclickerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" AutoClicker Multiplataforma")
        self.setFixedSize(500, 450)
        
        # Hotkeys
        self.clicking = False
        self.click_thread = None
        self.total_clicks = 0
        self.keyboard_listeners = []
        
        # Estilos modernos
        self.setStyleSheet("""
            QMainWindow { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c3e50, stop:1 #34495e); color: white; }
            QLabel { color: white; padding: 5px; }
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9); border: none; border-radius: 10px; color: white; padding: 12px; font-weight: bold; font-size: 14px; min-height: 45px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5dade2, stop:1 #3498db); }
            QPushButton:pressed { background: #2980b9; }
            QPushButton:disabled { background: #7f8c8d; }
            QSpinBox { background: #ecf0f1; border: 2px solid #bdc3c7; border-radius: 8px; padding: 8px; font-size: 14px; color: #2c3e50; min-height: 35px; }
        """)
        
        self.init_ui()
        self.setup_input()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        

        # SO detectado
        so_label = QLabel(f"{SYSTEM}")
        so_label.setStyleSheet("color: #2ecc71; font-size: 14px;")
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
        self.status_label = QLabel(" Listo")
        self.status_label.setFont(QFont("Segoe UI", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Botones principales
        buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton(" INICIAR")
        self.start_btn.clicked.connect(self.start_clicking)
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton(" DETENER")
        self.stop_btn.clicked.connect(self.stop_clicking)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        layout.addLayout(buttons_layout)
        
        # Info hotkeys SEGÚN SO
        if IS_WINDOWS and KEYBOARD_AVAILABLE:
            hotkey_info = QLabel(" F1=INICIAR F2=DETENER ESC=EMERGENCIA\n(Hotkeys GLOBALES)")
            hotkey_info.setStyleSheet("color: #2ecc71; font-size: 12px;")
        else:
            hotkey_info = QLabel(" F1=INICIAR F2=DETENER ESC=EMERGENCIA\n(Clic en ventana primero)")
            hotkey_info.setStyleSheet("color: #f39c12; font-size: 12px;")
        hotkey_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(hotkey_info)
        
        # Seguridad
        info = QLabel(" Esquina sup.izq. = FAILSAFE de emergencia")
        info.setStyleSheet("color: #e74c3c; font-size: 11px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
    
    def setup_input(self):
        """Configura hotkeys según SO"""
        if IS_WINDOWS and KEYBOARD_AVAILABLE:
            self.setup_global_hotkeys()
        else:
            self.setFocusPolicy(Qt.StrongFocus)
            print("🐧 Hotkeys en ventana activados")
    
    def setup_global_hotkeys(self):
        """Hotkeys GLOBALES para Windows"""
        def on_f1():
            if not self.clicking:
                self.start_clicking()
        
        def on_f2():
            self.stop_clicking()
        
        def on_esc():
            self.emergency_stop()
        
        self.keyboard_listeners = [
            keyboard.add_hotkey('f1', on_f1),
            keyboard.add_hotkey('f2', on_f2),
            keyboard.add_hotkey('esc', on_esc)
        ]
        print(" Hotkeys GLOBALES Windows activados")
    
    def keyPressEvent(self, event):
        """Hotkeys en ventana (Linux/macOS/Windows fallback)"""
        if IS_WINDOWS and KEYBOARD_AVAILABLE:
            return super().keyPressEvent(event)
        
        key = event.key()
        if key == Qt.Key_F1 and not self.clicking:
            self.start_clicking()
            print(" F1 - INICIADO")
        elif key == Qt.Key_F2:
            self.stop_clicking()
            print(" F2 - DETENIDO")
        elif key == Qt.Key_Escape:
            self.emergency_stop()
            print("ESC - EMERGENCIA")
        
        super().keyPressEvent(event)
    
    def start_clicking(self):
        if self.clicking:
            return

        # ANTI-CENTRADO: desactiva foco y limpia eventos de Qt
        self.setFocusPolicy(Qt.NoFocus)
        QApplication.processEvents()

        cps = self.cps_spin.value()
        self.click_thread = ClickThread()
        self.click_thread.set_interval(1.0 / cps)
        self.click_thread.clicks_updated.connect(self.update_clicks)

        self.clicking = True
        self.total_clicks = 0
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText(" Cliqueando...")
        self.click_thread.start()
    
    def stop_clicking(self):
        if self.click_thread:
            self.click_thread.running = False
            self.click_thread.quit()
            self.click_thread.wait(1000)
        self.clicking = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(" Detenido")

        self.setFocusPolicy(Qt.StrongFocus)

    def emergency_stop(self):
        self.stop_clicking()
        self.status_label.setText("Emergencia")
    
    def update_clicks(self, clicks):
        self.total_clicks = clicks
        self.clicks_label.setText(f"Clics: {clicks:,}")
    
    def closeEvent(self, event):
        if hasattr(self, 'keyboard_listeners'):
            for listener in self.keyboard_listeners:
                keyboard.remove_hotkey(listener)
        self.stop_clicking()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AutoclickerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
