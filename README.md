# AutoClicker Multiplataforma

Auto-clicker de escritorio multiplataforma construido con Python y PySide6 (Qt). Hace clic automáticamente en la posición actual del mouse a una frecuencia configurable, con hotkeys para iniciar, detener y parada de emergencia.

## Descargas rápidas

| Plataforma | Descargar |
|------------|-----------|
| Windows | [AutoClicker.exe](https://github.com/Cesar-RG/AutoClicker/releases/latest/download/AutoClicker.exe) |
| Linux | [AutoClicker](https://github.com/Cesar-RG/AutoClicker/releases/latest/download/AutoClicker) |

> Si los enlaces no funcionan, ve a [Releases](https://github.com/Cesar-RG/AutoClicker/releases) o descarga el artefacto desde la pestaña **Actions** del repositorio.

## Funcionalidades

- **Multiplataforma** -- Windows, Linux y macOS
- **Frecuencia configurable** -- de 1 a 20 clics por segundo
- **Control por hotkeys** -- F1 (iniciar), F2 (detener), Esc (parada de emergencia)
- **Hotkeys globales en Windows** -- funcionan aunque la ventana no tenga el foco (librería `keyboard`)
- **Hotkeys de ventana en Linux/macOS** -- funcionan con la ventana enfocada
- **Contador de clics en vivo** -- muestra el total de clics en tiempo real
- **Failsafe** -- mueve el mouse a la esquina superior izquierda para detener todo instantáneamente
- **Interfaz moderna** -- tema oscuro con degradados, botones y campos estilizados

## Captura de pantalla

La ventana de la aplicación muestra:
- Sistema operativo detectado
- Selector de clics por segundo (CPS)
- Contador de clics en vivo
- Botones Iniciar / Detener
- Referencia de hotkeys e info de failsafe

## Requisitos

- Python 3.12+
- [PySide6](https://pypi.org/project/PySide6/) -- interfaz gráfica (Qt)
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) -- automatización de clics
- [keyboard](https://pypi.org/project/keyboard/) -- hotkeys globales (solo Windows, opcional en otros SO)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Cesar-RG/AutoClicker.git
cd AutoClicker
```

### 2. Instalar uv (recomendado)

[uv](https://docs.astral.sh/uv/) es un gestor de paquetes rápido para Python. Instálalo y sincroniza las dependencias:

```bash
# Instalar uv (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh
# En Windows:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

uv sync
```

Alternativamente, con pip + venv:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install PySide6 pyautogui keyboard
```

> **Nota:** En Linux, la librería `keyboard` requiere `sudo` para hotkeys globales. La app usa hotkeys de ventana como respaldo automático.
>
> **Wayland:** `pyautogui` y `keyboard` necesitan X11. Si usas Linux + Wayland, cierra sesión y elige "GNOME on Xorg" (o similar). La app mostrará una advertencia si detecta Wayland.

## Uso

Ejecutar la aplicación:

```bash
uv run python autoclicker.py
# O directamente:
uv run autoclicker
```

### Controles

| Acción                | Hotkey | Botón    |
|-----------------------|--------|----------|
| Iniciar clics         | F1     | INICIAR  |
| Detener clics         | F2     | DETENER  |
| Parada de emergencia  | Esc    | --       |

### Modos de hotkeys

- **Windows (global):** Las hotkeys funcionan en todo el sistema, incluso sin enfocar la ventana. Requiere la librería `keyboard`.
- **Linux / macOS (ventana):** Las hotkeys solo funcionan con la ventana enfocada. Haz clic en la ventana antes de usar las hotkeys.

### Failsafe

El failsafe de PyAutoGUI está activado por defecto. Mueve el cursor a la **esquina superior izquierda** de la pantalla para abortar todos los clics inmediatamente.

## Compilar ejecutables

El proyecto incluye workflows de GitHub Actions para Windows y Linux:

```
.github/workflows/
├── build-windows.yml    # Compilar .exe para Windows
└── build-linux.yml      # Compilar binario para Linux
```

Ambos usan [PyInstaller](https://pypi.org/project/PyInstaller/) mediante `uv`:

```bash
uv run pyinstaller --onefile --windowed --name AutoClicker --noconsole autoclicker.py
```

Para descargar un ejecutable compilado, ve a la pestaña **Actions** del repositorio, selecciona la ejecución más reciente y descarga el artefacto.

## Estructura del proyecto

```
AutoClicker/
├── autoclicker.py               # Aplicación principal
├── pyproject.toml               # Configuración y dependencias (uv)
├── tests/
│   └── test_autoclicker.py      # Tests unitarios
├── .github/
│   └── workflows/
│       ├── build-windows.yml    # CI: .exe para Windows
│       └── build-linux.yml      # CI: binario para Linux
├── .gitignore
└── README.md
```

## Cómo funciona

1. **ClickThread** -- subclase de `QThread` que ejecuta un bucle haciendo clic en la posición actual del mouse con `pyautogui.click()` en el intervalo configurado.
2. **AutoclickerWindow** -- `QMainWindow` principal que provee la interfaz, gestiona el hilo de clics y maneja la entrada de hotkeys.
3. Al iniciar, la app detecta el sistema operativo y configura las hotkeys según corresponda (globales en Windows, de ventana en otros SO).

## Releases automáticos

Al empujar un tag con formato `v*` (ej. `v1.0.0`), GitHub Actions compila los binarios para Windows y Linux y los publica automáticamente en [Releases](https://github.com/Cesar-RG/AutoClicker/releases):

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Licencia

[MIT](LICENSE) -- haz lo que quieras con el código.
