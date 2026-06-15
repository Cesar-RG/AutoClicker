# AutoClicker para Windows y Linux

Auto-clicker de escritorio para Windows y Linux construido con Python y PySide6 (Qt). Hace clic automaticamente en la posicion actual del mouse a una frecuencia configurable, con hotkeys para iniciar, detener y parada de emergencia.

## Descargas rapidas

| Plataforma | Descargar |
|------------|-----------|
| Windows | [AutoClicker.exe](https://github.com/Cesar-RG/AutoClicker/releases/latest/download/AutoClicker.exe) |

> Si los enlaces no funcionan, ve a [Releases](https://github.com/Cesar-RG/AutoClicker/releases) o descarga el artefacto desde la pestana **Actions** del repositorio.

## Funcionalidades

- **Windows y Linux** -- probado en ambos sistemas
- **Frecuencia configurable** -- de 1 a 20 clics por segundo
- **Control por hotkeys** -- F1 (iniciar), F2 (detener), Esc (parada de emergencia)
- **Hotkeys globales en Windows** -- funcionan aunque la ventana no tenga el foco (libreria `keyboard`)
- **Hotkeys de ventana en Linux** -- funcionan con la ventana enfocada
- **Contador de clics en vivo** -- muestra el total de clics en tiempo real
- **Failsafe** -- mueve el mouse a la esquina superior izquierda para detener todo instantaneamente
- **Interfaz moderna** -- tema oscuro con degradados, botones y campos estilizados

## Captura de pantalla

La ventana de la aplicacion muestra:
- Sistema operativo detectado
- Selector de clics por segundo (CPS)
- Contador de clics en vivo
- Botones Iniciar / Detener
- Referencia de hotkeys e info de failsafe

## Requisitos

- Python 3.12+
- [PySide6](https://pypi.org/project/PySide6/) -- interfaz grafica (Qt)
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) -- automatizacion de clics
- [keyboard](https://pypi.org/project/keyboard/) -- hotkeys globales (solo Windows, opcional en Linux)

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/Cesar-RG/AutoClicker.git
cd AutoClicker
```

### 2. Instalar uv (recomendado)

[uv](https://docs.astral.sh/uv/) es un gestor de paquetes rapido para Python:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

Alternativamente, con pip + venv:

```bash
python -m venv venv
source venv/bin/activate  # Linux
pip install PySide6 pyautogui keyboard
```

> **Nota:** En Linux, la libreria `keyboard` requiere `sudo` para hotkeys globales. La app usa hotkeys de ventana como respaldo automatico.
>
> **Wayland:** `pyautogui` y `keyboard` necesitan X11. Si usas Linux + Wayland, cierra sesion y elige "GNOME on Xorg" (o similar). La app mostrara una advertencia si detecta Wayland.

## Uso

Ejecutar la aplicacion:

```bash
uv run python autoclicker.py
# O directamente:
uv run autoclicker
```

### Controles

| Accion                | Hotkey | Boton    |
|-----------------------|--------|----------|
| Iniciar clics         | F1     | INICIAR  |
| Detener clics         | F2     | DETENER  |
| Parada de emergencia  | Esc    | --       |

### Modos de hotkeys

- **Windows (global):** Las hotkeys funcionan en todo el sistema, incluso sin enfocar la ventana. Requiere la libreria `keyboard`.
- **Linux (ventana):** Las hotkeys solo funcionan con la ventana enfocada. Haz clic en la ventana antes de usarlas.

### Failsafe

El failsafe de PyAutoGUI esta activado por defecto. Mueve el cursor a la **esquina superior izquierda** de la pantalla para abortar todos los clics inmediatamente.

## Compilar ejecutables

El proyecto incluye workflows de GitHub Actions para Windows y Linux:

```
.github/workflows/
├── build-windows.yml    # Compilar .exe para Windows
└── build-linux.yml      # Compilar binario para Linux
```

Ambos usan [PyInstaller](https://pypi.org/project/PyInstaller/) mediante `uv`:

```bash
uv run pyinstaller --onefile --windowed --name AutoClicker autoclicker.py
```

Para descargar un ejecutable compilado, ve a la pestana **Actions** del repositorio, selecciona la ejecucion mas reciente y descarga el artefacto.

## Estructura del proyecto

```
AutoClicker/
├── autoclicker.py                  # Punto de entrada (wrapper)
├── autoclicker/
│   ├── __init__.py                 # main(): crea la aplicacion Qt
│   ├── config.py                   # Deteccion SO, logging, tema visual
│   ├── thread.py                   # ClickThread (QThread con pyautogui)
│   ├── hotkeys_windows.py          # Hotkeys globales (keyboard)
│   ├── hotkeys_unix.py             # Hotkeys de ventana (Linux)
│   └── window.py                   # AutoclickerWindow (UI principal)
├── pyproject.toml                  # Configuracion y dependencias (uv)
├── tests/
│   └── test_autoclicker.py         # Tests unitarios (pytest + pytest-qt)
├── .github/
│   └── workflows/
│       ├── build-windows.yml       # CI: .exe para Windows
│       └── build-linux.yml         # CI: binario para Linux
├── .gitignore
└── README.md
```

## Como funciona

1. **ClickThread** -- subclase de `QThread` que ejecuta un bucle haciendo clic con `pyautogui.click()` en el intervalo configurado. Se detiene con `requestInterruption()`.
2. **AutoclickerWindow** -- `QMainWindow` principal que provee la interfaz, gestiona el hilo de clics y maneja las hotkeys (globales en Windows, de ventana en Linux).
3. Al iniciar, la app detecta el sistema operativo y carga el modulo de hotkeys correspondiente.

## Releases automaticos

Al empujar un tag con formato `v*` (ej. `v1.0.0`), GitHub Actions compila el .exe para Windows y lo publica en [Releases](https://github.com/Cesar-RG/AutoClicker/releases):

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Licencia

[MIT](LICENSE) -- haz lo que quieras con el codigo.
