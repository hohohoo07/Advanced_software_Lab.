@echo off
setlocal
cd /d "%~dp0"
echo [1/2] Preparing a local Python environment...
if exist ".venv\Scripts\python.exe" goto install
py -3 -m venv .venv
if errorlevel 1 goto failed
:install
echo [2/2] Installing the practice packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Setup complete. Open RUN_PRACTICE.bat next.
pause
exit /b 0
:failed
echo.
echo Setup failed. Check that Python and the py launcher are installed.
echo The first package installation requires an internet connection.
pause
exit /b 1
