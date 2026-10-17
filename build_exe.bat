@echo off
setlocal enabledelayedexpansion
title JiraDesk — Automated Windows .EXE Builder

echo ========================================================
echo         JiraDesk Windows Executable Builder
echo ========================================================
echo.

python --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    py --version >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Python is required to build JiraDesk.
        echo Please install Python 3.9+ from https://www.python.org/
        pause
        exit /b 1
    )
    set PY_CMD=py
) else (
    set PY_CMD=python
)

echo [1/3] Checking PyInstaller dependency...
%PY_CMD% -m pip show pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing PyInstaller automatically via pip...
    %PY_CMD% -m pip install --upgrade pip
    %PY_CMD% -m pip install pyinstaller
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install PyInstaller. Please check internet connection.
        pause
        exit /b 1
    )
)
echo [OK] PyInstaller is installed.

echo.
echo [2/3] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/3] Compiling standalone executable...
echo Building directory distribution for Inno Setup...
%PY_CMD% -m PyInstaller --noconfirm --onedir --windowed --name "JiraDesk" --icon "assets\app_icon.ico" --add-data "assets;assets" main.py

echo.
echo Building portable single-file executable...
%PY_CMD% -m PyInstaller --noconfirm --onefile --windowed --name "JiraDesk_Portable" --icon "assets\app_icon.ico" --add-data "assets;assets" main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   [SUCCESS] Executable Build Completed!
    echo ========================================================
    echo   - Folder app:     dist\JiraDesk\JiraDesk.exe
    echo   - Single-file:    dist\JiraDesk_Portable.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] PyInstaller compilation encountered an error.
)

pause
