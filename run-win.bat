@echo off

REM Check if Python 3.12.10 or 3.12.11 is available
where python >nul 2>nul || (echo Python must be in PATH.& exit /b 1)
py -3.12 -c "import sys; exit(0 if sys.version_info[:3] in [(3,12,10),(3,12,11)] else 1)" || (
    echo Python 3.12.10 or 3.12.11 required.
    py -3.12 --version
    exit /b 1
)

REM Create venv with the right Python
IF NOT EXIST venv (
  echo Creating virtual environment...
  py -3.12 -m venv venv
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat || (echo Failed to activate venv.& exit /b 1)

REM show which python is used
python --version

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Run package module, not src
echo Starting application...
python -m super_mario_motion.main

pause
