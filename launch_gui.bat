@echo off
REM Monthly Report Builder - GUI Launcher
REM Double-click this file to launch the reporting tool

echo Starting Monthly Report Builder...
echo.

REM Check if executable exists
if exist "Monthly_Report_Builder.exe" (
    echo Launching GUI...
    start "" "Monthly_Report_Builder.exe"
) else (
    echo ERROR: Monthly_Report_Builder.exe not found!
    echo Please ensure the executable is in the same folder as this launcher.
    echo.
    pause
)