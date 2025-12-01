.DEFAULT_GOAL := run

PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip

UNAME_S := $(shell uname -s)

ICON = src/super_mario_motion/images/icon.png

# Create virtual environment and install dependencies
venv: requirements.txt
	python3.12 -m venv venv
	$(PIP) install -r requirements.txt

# Runs our program, checks if we are in a virtual environment
run: venv
	PYTHONPATH=src $(PYTHON) -m super_mario_motion.main

train: venv
	PYTHONPATH=src $(PYTHON) -m super_mario_motion.train

test: venv
	PYTHONPATH=src $(PYTHON) -m pytest

# Builds project into a single binary with platform-specific icon
pyinstaller: venv
	PYTHONPATH=src $(PYTHON) -m PyInstaller --name SuperMarioMotion --windowed --icon=$(ICON) src/super_mario_motion/main.py
