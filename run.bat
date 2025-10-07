@echo off
:: -------------------------------
:: Configuration
:: -------------------------------
set /p HOST="Enter Raspberry Pi IP address: "
set USER=master
set REMOTE_DIR=ece4191-s2-2025-r21/
set REMOTE_SCRIPT=script/main.py
set LOCAL_SCRIPT=camera_vision/camera_processing.py

:: List of possible virtual environment paths
set VENV_LIST=.venv\Scripts\activate.bat;venv\Scripts\activate.bat;env\Scripts\activate.bat

:: -------------------------------
:: Find a valid virtual environment
:: -------------------------------
set FOUND_VENV=
for %%v in (%VENV_LIST%) do (
    if exist "%%v" (
        set FOUND_VENV=%%v
        goto :VENV_FOUND
    )
)

:: If no venv found
echo ERROR: Could not find a virtual environment! Checked: %VENV_LIST%
pause
exit /b 1

:VENV_FOUND
echo Using virtual environment: %FOUND_VENV%

:: -------------------------------
:: Run remote script in new terminal
:: -------------------------------
start cmd /k ssh -t %USER%@%HOST% "cd %REMOTE_DIR% && python3 %REMOTE_SCRIPT%"

:: -------------------------------
:: Run local script in new terminal using virtual environment
:: -------------------------------
start cmd /k "call %FOUND_VENV% && python %LOCAL_SCRIPT%"

echo --- Both scripts started ---
pause