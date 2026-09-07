@echo off
:: ============================================================================
::  PERSONA 5: THE PHANTOM TEXT PURGE // DESKTOP LAUNCHER
::  Launches pythonw smoothly in background without keeping terminal window open
:: ============================================================================
cd /d "%~dp0"

set "TARGET_SCRIPT=%~dp0remove_paragraph.py"

:: Check pythonw in system PATH
where pythonw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pythonw "%TARGET_SCRIPT%"
    exit /b 0
)

:: Check pyw (standard Python Launcher) in system PATH
where pyw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pyw "%TARGET_SCRIPT%"
    exit /b 0
)

:: Check common local Python installs
for %%V in (Python313 Python312 Python311 Python310) do (
    if exist "%LOCALAPPDATA%\Programs\Python\%%V\pythonw.exe" (
        start "" "%LOCALAPPDATA%\Programs\Python\%%V\pythonw.exe" "%TARGET_SCRIPT%"
        exit /b 0
    )
)

:: Fallback: Search python in system PATH
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" python "%TARGET_SCRIPT%"
    exit /b 0
)

:: Fallback: Search py in system PATH
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" py "%TARGET_SCRIPT%"
    exit /b 0
)

echo [ERROR] Python was not found on your system!
echo Target: %TARGET_SCRIPT%
echo Please ensure Python is installed and added to PATH.
pause
exit /b 1
