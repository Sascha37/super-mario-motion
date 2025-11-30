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

doc:
	sphinx-apidoc -f -o docs/api src/super_mario_motion
	sphinx-build -b html docs docs/_build/html
