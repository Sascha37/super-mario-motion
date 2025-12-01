.DEFAULT_GOAL := run

PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip

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

doc: venv
	$(PYTHON) -m sphinx.ext.apidoc -f -o docs/api src/super_mario_motion
	$(PYTHON) -m sphinx -b html docs docs/_build/html

docw:
	sphinx-apidoc -f -o docs/api src/super_mario_motion
	sphinx-build -b html docs docs/_build/html

# Builds project into a single binary
pyinstaller: venv
	$(PYTHON) -m PyInstaller src/super_mario_motion/main.spec
