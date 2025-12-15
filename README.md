# Super Mario Motion ![GitHub License](https://img.shields.io/github/license/Sascha37/super-mario-motion) ![GitHub last commit](https://img.shields.io/github/last-commit/Sascha37/super-mario-motion) [![Run Unit Test via Pytest](https://github.com/Sascha37/super-mario-motion/actions/workflows/run_test.yml/badge.svg)](https://github.com/Sascha37/super-mario-motion/actions/workflows/run_test.yml)

An application written in Python that uses OpenCV alongside MediaPipe to translate your movements,
captured by your webcam, into inputs for *Super Mario Bros. 1*.

This software is designed to be used alongside an NES emulator running the original Super Mario
Bros. game.
We do not provide the emulator or the game.

If you don't have an emulator, the application also supports sending inputs to a web version of the game.

## Table of Contents

- [Requirements](#requirements)
- [Downloads](#downloads)
- [Build app and edit source code](#build-app-and-edit-source-code)
    - [On macOS and Linux](#on-macos-and-linux-using-make)
    - [On Windows](#on-windows)
- [Usage](#usage)
- [Project Documentation](#project-documentation)
- [Compatibility](#compatibility)
- [License](#license)
- [Data Processing](#data-processing)

## Requirements
### For running the app
- **Webcam:** Any common USB-Webcam will do, make sure it is connected, otherwise the program will
  not be able to run

- (Optional) **NES Emulator**: Any of your choice. Recommended: default
  settings [RetroArch](https://www.retroarch.com/?page=platforms) using FCEUmm core
- (Optional) **ROM file**: You must provide your own legally obtained NES ROM. This repository does not
  include or link to any ROMs.

### For building the app

- **Python**: Version 3.12.11

- **Python-modules**: All required modules can be found in
  the [requirements.txt](https://github.com/Sascha37/super-mario-motion/blob/main/requirements.txt)
  file

## Downloads
Get the latest release of this application here:

https://github.com/Sascha37/super-mario-motion/releases/latest


## Build app and edit source code

### On macOS and Linux (using `make`)

If you want to start to work on the app, use:

```
git clone https://github.com/Sascha37/super-mario-motion.git
cd super-mario-motion/
make run
```

- `make run` will start the application
- `make pyinstaller` will build an executable (for the current os)
- `make train` builds the ml-model (needs training data)
- `make test` will run the pytest testsuite

To modify the source code, open the project in your preferred text editor or IDE.

Alternatively to using the makefile you can manually create a Python virtual environment and
install dependencies using pip. Look into
the [Makefile](https://github.com/Sascha37/super-mario-motion/blob/main/Makefile) of this project
for reference.

### On Windows

If you just want to **run** the program, execute the `run-win.bat` file.

If you want to **work with and modify this code**, open it in a code editor
like [PyCharm](https://www.jetbrains.com/pycharm/) and select the correct version of the python
interpreter (3.12.11 or 3.12.10)

## Usage

### Quick Start

- Start the program (either from source code or the standalone application).
- Select the version of the game you want to play (web or original).
- Select between `Simple` (designed to be used while sitting) or `Full-body`-mode (designed to be used while standing). 
- Inputs can only be sent to the game if the window of the game is in focus and the `Send Inputs`
  checkbox has been checked.

**For more information please press the `Help`-Button or [open this file](https://github.com/Sascha37/super-mario-motion/blob/main/docs/help/help_page.pdf)**

<p align="center">
    <img src="docs/screenshots/ss1.png" alt="Screenshot" height="730"/>
</p>

## Project Documentation

- Everything related to documentation can be found in the `docs/` folder.
    - For PDFs used as bullet points to discuss in the weekly meetings, see `docs/meetings/`
    - A comprehensive report, including weekly feature updates, can be found
      in [progress_documentation.md](https://github.com/Sascha37/super-mario-motion/blob/main/docs/progress_documentation.md)

## Compatibility

This project is being developed and tested on the following operating systems:

- **Windows 10** (22H2) and **Windows 11** (25H2)
- **macOS** (15.7.1 and 26.1)
- **Arch Linux** using Wayland and KDE Plasma

We aim to support all versions of Windows, macOS, and Linux.

If you encounter issues on any version, please leave an issue so we can investigate.

## License

This project is available under the GPL v3.0. See
the [LICENSE](https://github.com/Sascha37/super-mario-motion/blob/main/LICENSE) file for more info.

## Data Processing

### GUI Inputs (User Interaction)

#### What the user does
The user interacts with:
- Mode selection (`Simple`, `Full-body`, `Collect`)
- Preview selection (Webcam / Skeleton / Skeleton Only)
- Game selection
- Checkboxes (e.g. *Send Inputs*, *Debug*)
- Buttons (Start game, Start collecting)

#### What happens internally
- Every GUI interaction updates the **current program state**
- This state controls:
  - how movements are interpreted
  - what is shown on screen
  - whether inputs are sent to the game

#### What is stored?
- **Nothing is saved to disk**
- GUI inputs exist **only while the program is running**


### Webcam Input

#### What the program does with it
For every frame:
1. The image is analyzed to detect the user's body
2. The body pose is estimated (arms, legs, torso)
3. A simple pose label is determined (e.g. standing, jumping)
4. Optional visuals are created:
   - webcam image
   - webcam with skeleton overlay
   - skeleton only

#### What is stored?
- Webcam images are **not saved**
- All data is used **live only** and replaced by the next frame


### Collect Mode (Recording Data)

#### When does this happen?
- Only when the user activates **Collect mode**
- Used to create training data

#### What is recorded?
- The webcam is analyzed the same way as in normal mode
- Instead of showing results only:
  - movement data is converted into **numbers**
  - each set of numbers is linked to a pose name

#### What is saved?
- **CSV files** containing:
  - pose label (text)
  - numerical movement data

#### What is NOT saved?
- No images
- No video
- No screenshots


### Training (After Collecting)

- Collected CSV files are used to train a model
- The result is **one model file**

### What is stored?
- One trained model file
- No webcam data
- No GUI data
