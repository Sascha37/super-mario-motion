# Super Mario Motion ![GitHub License](https://img.shields.io/github/license/Sascha37/super-mario-motion) ![GitHub last commit](https://img.shields.io/github/last-commit/Sascha37/super-mario-motion) [![Run Unit Test via Pytest](https://github.com/Sascha37/super-mario-motion/actions/workflows/run_test.yml/badge.svg)](https://github.com/Sascha37/super-mario-motion/actions/workflows/run_test.yml)
An application written in Python that uses OpenCV alongside MediaPipe to translate your movements, captured by your webcam, into inputs for *Super Mario Bros. 1*.

This software is designed to be used alongside an NES emulator running the original Super Mario Bros. game.
We do not provide the emulator or the game.

## Table of Contents
- [Requirements](#requirements)
- [How to Run and Edit](#how-to-run-and-edit)
    - [On macOS and Linux](#on-macos-and-linux-using-make)
    - [On Windows](#on-windows)
- [Usage](#usage)
- [Project Documentation](#project-documentation)
- [Compatibility](#compatibility)
- [License](#license)

## Requirements
- **Python**: Version 3.12.11

- **Python-modules**: All required modules can be found in the [requirements.txt](https://github.com/Sascha37/super-mario-motion/blob/main/requirements.txt) file
- **Webcam:** Any common USB-Webcam will do, make sure it is connected, otherwise the program will not be able to run
- **NES Emulator**: Any of your choice. Recommended: default settings [RetroArch](https://www.retroarch.com/?page=platforms) using FCEUmm core 
- **ROM file**: You must provide your own legally obtained NES ROM. This repository does not include or link to any ROMs.
## How to Run and Edit
### On macOS and Linux (using `make`)
If you just want to run the program:
```
git clone https://github.com/Sascha37/super-mario-motion.git
cd super-mario-motion/
make run
```
To modify the source code, open the project in your preferred text editor or IDE.

Alternatively to using the makefile you can manually create a Python virtual environment and install dependencies using pip. Look into the [Makefile](https://github.com/Sascha37/super-mario-motion/blob/main/Makefile) of this project for reference.

### On Windows

If you just want to **run** the program, execute the `run-win.bat` file.

If you want to **work with and modify this code**, open it in a code editor like [PyCharm](https://www.jetbrains.com/pycharm/) and select the correct version of the python interpreter (3.12.11 or 3.12.10)

## Usage
### Quick Start
- Start the program (if you have not already done so and need help, see the previous step).
- Start the emulator with your game.
- You can now select, via the dropdown menu, either full body movement or simple movements (designed to be used while sitting on your chair).
- Inputs can only be sent to the game if the emulator window is in focus and the `Send Inputs` checkbox has been checked.

<p align="center">
    <img src="docs/screenshots/ss1.png" alt="Screenshot" height="400"/>
</p>

## Project Documentation
- Everything related to documentation can be found in the `docs/` folder.
    - For PDFs used as bullet points to discuss in the weekly meetings, see `docs/meetings/`
    - A comprehensive report, including weekly feature updates, can be found in [progress_documentation.md](https://github.com/Sascha37/super-mario-motion/blob/main/docs/progress_documentation.md)
## Compatibility
This project is being developed and tested on the following operating systems:
- **Windows 10** (22H2) and **Windows 11** (25H2)
- **macOS** (15.7.1 and 26.1)
- **Arch Linux** using Wayland and KDE Plasma

We aim to support all versions of Windows, macOS, and Linux.

If you encounter issues on any version, please leave an issue so we can investigate.

## License
This project is available under the GPL v3.0. See the [LICENSE](https://github.com/Sascha37/super-mario-motion/blob/main/LICENSE) file for more info.
