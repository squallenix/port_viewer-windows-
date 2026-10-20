@echo off
setlocal EnableDelayedExpansion
title Port Viewer - Windows EXE Builder

echo ========================================================
echo         Port Viewer - Standalone EXE Builder
echo ========================================================
echo.

:: 1. Detect Python
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PY_CMD=py"
    ) else (
        echo [ERROR] Python was not found on your system!
        echo Please download and install Python from https://www.python.org/downloads/
        echo Make sure to check the box: "Add python.exe to PATH"
        echo.
        pause
        exit /b 1
    )
)

echo [1/4] Found Python: %PY_CMD%
%PY_CMD% --version

:: 2. Check or create virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [2/4] Setting up Python virtual environment (.venv)...
    %PY_CMD% -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Virtual environment exists.
)

:: 3. Install required packages
echo [3/4] Installing required dependencies...
call .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
call .\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Ensure assets icon exists
if not exist "assets\icon.ico" (
    echo Generating application icons...
    call .\.venv\Scripts\python.exe generate_icon.py
)

:: 4. Build single-file executable using PyInstaller
echo [4/4] Building single-file executable (dist\PortViewer.exe)...
echo Please wait, this takes about 15-30 seconds...
echo.

call .\.venv\Scripts\pyinstaller.exe --noconsole --onefile --clean ^
    --name "PortViewer" ^
    --icon "assets\icon.ico" ^
    --add-data "assets;assets" ^
    --collect-all customtkinter ^
    main.py

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo  [SUCCESS] Build completed successfully!
    echo  Standalone executable created at:
    echo  dist\PortViewer.exe
    echo ========================================================
    echo.
    echo You can distribute 'dist\PortViewer.exe' directly to any Windows user!
) else (
    echo.
    echo [ERROR] Build failed. See logs above.
)

echo.
pause
