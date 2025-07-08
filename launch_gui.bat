@echo off
REM RBuilder - GUI Launcher
REM Double-click this file to launch the reporting tool

echo Starting RBuilder...
echo.

REM Check if executable exists
if exist "RBuilder.exe" (
    echo Launching GUI...
    start "" "RBuilder.exe"
) else (
    echo ERROR: RBuilder.exe not found!
    echo Please ensure the executable is in the same folder as this launcher.
    echo.
    pause
)