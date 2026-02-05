# Data Scavenger Deployment Guide

## 1. Prerequisites
* **Python 3.12+** must be installed.
* Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
* Ensure `nuitka` is installed (included in requirements).

## 2. Building the Executable
We use Nuitka to compile the Python source into a standalone Windows executable (`.exe`).

### Build Command
Run the build script from the project root:
```bash
python build.py
```
* This process may take 5-10 minutes depending on your hardware.
* **Note:** `pandas` and `openpyxl` are heavy libraries, so the initial build might be slow. Nuitka caches results for faster subsequent builds.

### Build Artifacts
* The output will be located in the `src.dist/` or `src.build/` directory (depending on Nuitka version).
* Look for `main.exe` (or `Data Scavenger.exe` if renamed).
* This single file contains everything needed to run the app. No Python installation is required on the target machine.

## 3. Distribution
1. **Copy:** Move `main.exe` to any folder on the target Windows machine.
2. **Config:** The app creates a `config.json` file in the same directory upon first run. You can pre-package a default `config.json` if you wish to enforce specific settings.
3. **Logs:** Logs are written to `app.log` in the same directory.

## 4. Troubleshooting
* **"Failed to execute script":** Check `app.log` or run via command line to see stderr output.
* **Missing DLLs:** If running on a clean Windows VM fails, ensure the Visual C++ Redistributable is installed (though Nuitka usually bundles necessary DLLs).
