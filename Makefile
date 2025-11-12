.DEFAULT_GOAL := run

PYTHON_CMD = python3.12
VENV_DIR = ./venv
PYTHON = $(VENV_DIR)/bin/python3
PIP = $(VENV_DIR)/bin/pip

# Create virtual environment and install dependencies
venv: requirements.txt
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON_CMD) -m venv $(VENV_DIR); \
	fi
	echo "Installing/updating dependencies from requirements.txt...";
	$(PIP) install -r requirements.txt

# Runs our program, checks if we are in a virtual environment
run: venv
	$(PYTHON) src/super-mario-motion/main.py

clean:
	rm -rf $(VENV_DIR)
