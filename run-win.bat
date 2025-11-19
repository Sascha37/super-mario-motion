@echo off

REM Check if Python 3.12 is available
where python >nul 2>nul || (echo Python must be in PATH.& exit /b 1)
py -3.12 -c "import sys; exit(0 if sys.version.startswith('3.12') else 1)" || (
    echo Python 3.12 required.
    exit /b 1
)

REM Create venv if not existing
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Run the project
echo Starting application...
python -m src.super_mario_motion.main

pause