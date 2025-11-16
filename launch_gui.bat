@echo off
REM Distillation Curve Interconversion GUI Launcher
REM Windows batch file to launch the application

echo.
echo ===================================================
echo  Distillation Curve Interconversion Tool
echo  D86 / D2887 / TBP Converter
echo ===================================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Launching with virtual environment...
    ".venv\Scripts\python.exe" distillation_converter_gui.py
) else (
    echo Virtual environment not found.
    echo Launching with system Python...
    python distillation_converter_gui.py
)

if errorlevel 1 (
    echo.
    echo ERROR: Failed to launch application
    echo.
    echo Troubleshooting:
    echo 1. Make sure Python is installed
    echo 2. Install dependencies: uv sync
    echo 3. Or install manually: pip install -r requirements.txt
    echo.
    pause
)
