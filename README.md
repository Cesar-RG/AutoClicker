# AutoClicker Multiplataforma

A cross-platform auto-clicker desktop application built with Python and PySide6 (Qt). It automatically clicks at your current mouse position at a configurable rate, with hotkey support for start, stop, and emergency stop.

## Features

- **Cross-platform** — works on Windows, Linux, and macOS
- **Configurable click rate** — 1 to 20 clicks per second
- **Hotkey controls** — F1 (start), F2 (stop), Esc (emergency stop)
- **Global hotkeys on Windows** — hotkeys work even when the app is not focused (via the `keyboard` library)
- **Window-scoped hotkeys on Linux/macOS** — hotkeys work when the app window is focused
- **Live click counter** — displays total clicks in real time
- **Failsafe** — move your mouse to the top-left corner of the screen to instantly stop clicking (PyAutoGUI failsafe)
- **Modern UI** — dark gradient theme with styled buttons and inputs

## Screenshots

The application window displays:
- Detected operating system
- Clicks-per-second selector
- Live click counter
- Start / Stop buttons
- Hotkey reference and failsafe info

## Requirements

- Python 3.12+
- [PySide6](https://pypi.org/project/PySide6/) — Qt bindings for the GUI
- [PyAutoGUI](https://pypi.org/project/PyAutoGUI/) — mouse click automation
- [keyboard](https://pypi.org/project/keyboard/) — global hotkeys (Windows only, optional on other platforms)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Cesar-RG/AutoClicker.git
cd AutoClicker
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install PySide6 pyautogui keyboard
```

> **Note:** On Linux/macOS, the `keyboard` library is optional. If it is not installed or cannot be imported, the app falls back to window-scoped hotkeys automatically.

## Usage

Run the application:

```bash
python autoclicker.py
```

### Controls

| Action         | Hotkey | Button     |
|----------------|--------|------------|
| Start clicking | F1     | INICIAR    |
| Stop clicking  | F2     | DETENER    |
| Emergency stop | Esc    | —          |

### Hotkey modes

- **Windows (global):** Hotkeys work system-wide, even when the AutoClicker window is not focused. Requires the `keyboard` library.
- **Linux / macOS (window):** Hotkeys only work when the AutoClicker window is focused. Click on the window first before using hotkeys.

### Failsafe

PyAutoGUI's failsafe is enabled by default. Move your mouse cursor to the **top-left corner** of the screen to immediately abort all clicking.

## Building a Windows executable

The project includes a GitHub Actions workflow that builds a standalone `.exe` on every push or PR to `main`:

```
.github/workflows/build-windows.yml
```

The workflow uses [PyInstaller](https://pypi.org/project/PyInstaller/) to produce a single-file executable:

```bash
pyinstaller --onefile --windowed --name AutoClicker --noconsole autoclicker.py
```

You can also run this command locally (after installing PyInstaller) to generate `dist/AutoClicker.exe`.

To download the built executable, go to the **Actions** tab in the GitHub repository, select the latest successful workflow run, and download the **AutoClicker-Windows** artifact.

## Project Structure

```
AutoClicker/
├── autoclicker.py               # Main application (single-file)
├── .github/
│   └── workflows/
│       └── build-windows.yml    # CI workflow to build Windows .exe
├── .gitignore
└── README.md
```

## How It Works

1. **ClickThread** — a `QThread` subclass that runs a loop clicking at the current mouse position using `pyautogui.click()` at the configured interval.
2. **AutoclickerWindow** — the main `QMainWindow` that provides the UI, manages the click thread, and handles hotkey input.
3. On startup, the app detects the operating system and configures hotkeys accordingly (global on Windows, window-scoped elsewhere).

## License

This project does not currently specify a license. Contact the repository owner for usage terms.
