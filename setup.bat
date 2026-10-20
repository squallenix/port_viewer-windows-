@echo off
setlocal EnableDelayedExpansion
title Port Viewer - Windows Installer / Setup

echo ========================================================
echo       Port Viewer - Windows One-Click Installer
echo ========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set "PY_CMD=py"
    ) else (
        echo [ERROR] Python is not installed or not in your PATH.
        echo Please install Python 3.10+ from https://www.python.org/
        pause
        exit /b 1
    )
)

echo [1/3] Initializing environment...
if not exist ".venv\Scripts\python.exe" (
    %PY_CMD% -m venv .venv
)

echo [2/3] Installing dependencies...
call .\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet

if not exist "assets\icon.ico" (
    call .\.venv\Scripts\python.exe generate_icon.py
)

:: Run security and module verification
echo [3/3] Running security self-checks...
call .\.venv\Scripts\python.exe -m unittest tests\test_port_viewer.py

echo.
echo ========================================================
echo Installation and verification complete!
echo.
echo Options:
echo   1. Launch Port Viewer now (from Python)
echo   2. Build standalone PortViewer.exe (PyInstaller)
echo   3. Create a Windows Desktop Shortcut
echo   4. Exit
echo ========================================================
set /p CHOICE="Select an option (1-4) [default: 1]: "

if "%CHOICE%"=="" set CHOICE=1
if "%CHOICE%"=="1" (
    start "" .\.venv\Scripts\pythonw.exe main.py
    exit /b 0
)
if "%CHOICE%"=="2" (
    call build_exe.bat
    exit /b 0
)
if "%CHOICE%"=="3" (
    echo Creating Desktop shortcut...
    powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\Port Viewer.lnk'); $s.TargetPath = '%~dp0run.bat'; $s.WorkingDirectory = '%~dp0'; $s.IconLocation = '%~dp0assets\icon.ico'; $s.Save()"
    echo Shortcut created on your Desktop!
    pause
    exit /b 0
)

exit /b 0
