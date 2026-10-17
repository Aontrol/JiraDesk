@echo off
setlocal enabledelayedexpansion
title JiraDesk — Automated One-Click Installer & Executable Builder

echo ========================================================
echo       JiraDesk Master Build: Executable + Inno Setup
echo ========================================================
echo.

echo [Step 1/2] Building Windows Executables with PyInstaller...
call "%~dp0build_exe.bat"

if not exist "%~dp0dist\JiraDesk\JiraDesk.exe" (
    echo.
    echo [ERROR] PyInstaller build failed or dist\JiraDesk\JiraDesk.exe does not exist.
    pause
    exit /b 1
)

echo.
echo [Step 2/2] Locating Inno Setup Compiler (ISCC.exe)...

set ISCC_PATH=

where iscc >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "ISCC_PATH=iscc"
    goto CompileInstaller
)

if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    goto CompileInstaller
)

if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    goto CompileInstaller
)

if exist "%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe"
    goto CompileInstaller
)

if exist "%ProgramFiles%\Inno Setup 5\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles%\Inno Setup 5\ISCC.exe"
    goto CompileInstaller
)

if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
    goto CompileInstaller
)

echo.
echo --------------------------------------------------------
echo [NOTICE] Inno Setup compiler (ISCC.exe) was not detected!
echo --------------------------------------------------------
echo Good news: Your standalone executables are ALREADY ready to use:
echo   - Portable Single-File App: dist\JiraDesk_Portable.exe
echo   - Folder App:               dist\JiraDesk\JiraDesk.exe
echo.
echo If you would like to generate the Windows Setup Wizard (installer):
echo 1. Download free Inno Setup (4 MB) from: https://jrsoftware.org/isdl.php
echo 2. Install Inno Setup and re-run this script!
echo --------------------------------------------------------
echo.
pause
exit /b 0

:CompileInstaller
echo Found Inno Setup Compiler at: "!ISCC_PATH!"
echo Compiling installer.iss...
"!ISCC_PATH!" "%~dp0installer.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo   [ALL DONE] Inno Setup Installer Successfully Built!
    echo ========================================================
    echo   Setup Installer:  Output\JiraDesk_Setup_v1.0.exe
    echo   Portable App:     dist\JiraDesk_Portable.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Inno Setup compilation encountered an issue.
)

pause
