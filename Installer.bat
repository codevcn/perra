@echo off
REM Compatibility wrapper — delegates to setup.bat / scripts/setup_manager.py
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\setup_manager.py %*
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        python scripts\setup_manager.py setup-all %*
    ) else (
        echo [!] Python 3.10+ was not found on PATH.
        echo [!] Install Python 3.10+ or use PerraSetup-*-win64.exe from https://github.com/codevcn/perra/releases
        pause
        exit /b 1
    )
)
