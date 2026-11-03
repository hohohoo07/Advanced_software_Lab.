@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto menu
echo Run SETUP.bat first.
pause
exit /b 1
:menu
echo.
echo 1. Read and play the video
echo 2. Frame difference
echo 3. Background subtraction
echo 4. Motion tracking and export
echo Q. Quit
set "practice_choice="
set /p "practice_choice=Choose 1-4 or Q: "
if /i "%practice_choice%"=="Q" exit /b 0
set "practice_script="
if "%practice_choice%"=="1" set "practice_script=01_read_video.py"
if "%practice_choice%"=="2" set "practice_script=02_frame_difference.py"
if "%practice_choice%"=="3" set "practice_script=03_background_subtraction.py"
if "%practice_choice%"=="4" set "practice_script=04_motion_tracking.py"
if not defined practice_script goto menu
echo Press q in the video window to stop playback.
".venv\Scripts\python.exe" "%practice_script%"
pause
goto menu
