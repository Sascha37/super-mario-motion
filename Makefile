.DEFAULT_GOAL := run

PYTHON = ./venv/bin/python3
PIP = ./venv/bin/pip

# Create virtual environment and intall dependencies
venv: requirements.txt
	python3.12 -m venv venv
	$(PIP) install -r requirements.txt

# Runs our program, checks if we are in a virual environment
run: venv
	$(PYTHON) src/super-mario-motion/main.py

train: venv
	$(PYTHON) src/super-mario-motion/train.py
