@echo off
setlocal EnableDelayedExpansion
title Port Viewer

:: Check Python
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

:: Setup venv if missing
if not exist ".venv\Scripts\python.exe" (
    echo [Setup] Creating virtual environment...
    %PY_CMD% -m venv .venv
    echo [Setup] Installing dependencies...
    call .\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
)

:: Ensure icon exists
if not exist "assets\icon.ico" (
    call .\.venv\Scripts\python.exe generate_icon.py
)

:: Run the application
start "" .\.venv\Scripts\pythonw.exe main.py
if %ERRORLEVEL% neq 0 (
    call .\.venv\Scripts\python.exe main.py
)
