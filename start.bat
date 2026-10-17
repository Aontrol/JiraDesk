@echo off
setlocal
title JiraDesk — Personal Workflow Tracker

echo ========================================================
echo          Starting JiraDesk Desktop Application...
echo ========================================================

where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pythonw "%~dp0main.py"
    exit /b 0
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" python "%~dp0main.py"
    exit /b 0
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" py "%~dp0main.py"
    exit /b 0
)

echo.
echo [ERROR] Python was not found on your system!
echo Please install Python 3.9+ from https://www.python.org/
echo Make sure to check "Add Python to PATH" during installation.
echo.
pause
