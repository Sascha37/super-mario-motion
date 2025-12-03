"""
Utility module for initializing RetroArch paths, validating configuration,
building platform-specific launch commands, and starting the selected game
(RetroArch, custom executable, or web version).
"""

import json
import subprocess
import webbrowser
from pathlib import Path
from sys import platform

from super_mario_motion.state import StateManager


module_log_prefix = "[Launcher]"

exe, core = None, None

def validate_path(path):
    """Validate that a given path exists and update the global flag.

    Prints an info message and sets `retro_paths_valid = False` if the
    path does not exist.

    Args:
        path (Path): File or directory path to validate.
    """
    global retro_paths_valid

    if not path.exists():
        print(
            f"{module_log_prefix} {path}, Path/File does not exist, please "
            f"edit the config at {config_path}"
            )
        return False
    else:
        print(f"{module_log_prefix} {path}, Path/File found.")
        return True


def init():
    global config_retroarch_path, config_rom_path, config_custom_path
    global retroarch_path, rom_path, custom_path, retro_paths_valid
    global custom_path_valid, config_path

    config_path = StateManager.get_config_path()

    config_retroarch_path = (
        json.loads(Path(config_path).read_text())[
            "emu-path"]
    )

    config_rom_path = (
        json.loads(Path(config_path).read_text())[
            "rom-path"]
    )

    config_custom_path = (
        json.loads(Path(config_path).read_text())[
            "custom-game-path"]
    )

    retroarch_path = Path(config_retroarch_path)
    rom_path = Path(config_rom_path)
    custom_path = Path(config_custom_path)

    retro_paths_valid = validate_path(retroarch_path) and validate_path(rom_path)
    custom_path_valid = validate_path(custom_path)

def get_command(platform_):
    """Build the RetroArch launch command for the given platform.

    Selects the correct executable and NES core depending on the
    OS platform string and returns a command list usable with
    `subprocess.run`.

    Args:
        platform_ (str): Platform identifier (e.g. 'linux', 'darwin', 'win32').

    Returns:
        list[str]: Command and arguments to launch RetroArch with the ROM.

    Raises:
        ValueError: If the platform is unknown.
    """
    global exe, core
    match platform_:
        case "linux":
            exe = retroarch_path / "retroarch.sh"
            core = retroarch_path / "cores" / "fceumm_libretro.so"
        case "darwin":
            exe = (retroarch_path / "RetroArch.app" / "Contents" / "MacOS" /
                   "RetroArch")
            core = retroarch_path / "cores" / "fceumm_libretro.dylib"
        case "win32":
            exe = retroarch_path / "retroarch.exe"
            core = retroarch_path / "cores" / "fceumm_libretro.dll"
        case _:
            raise ValueError(
                f"{module_log_prefix} Unknown platform: {platform_}"
                )

    return [
        str(exe),
        "-L",
        str(core),
        str(rom_path)
        ]


def launch_game():
    """Launch the configured game via RetroArch if all paths are valid.

    Uses `get_command` with the current platform and runs RetroArch
    via `subprocess.run`. Prints error messages if launch fails.
    """
    scheme = StateManager.get_control_scheme()
    if scheme == "supermarioplay (Web)":
        webbrowser.open("https://supermarioplay.com")
        return

    if not retro_paths_valid and not custom_path_valid:
        print(
            f"{module_log_prefix} Could not start the game. Invalid paths "
            f"set. Please edit the config."
            )
        return
    if scheme == "Original (RetroArch)":
        try:
            subprocess.run(
                get_command(platform), cwd=str(retroarch_path),
                check=True
                )
        except subprocess.CalledProcessError:
            print(f"{module_log_prefix} Failed to open the game.")
        except FileNotFoundError as e:
            print(f"{module_log_prefix} Could not find launchable file: {e}")

    if scheme == "Custom":
        try:
            subprocess.run(custom_path, check=True)
        except subprocess.CalledProcessError:
            print(f"{module_log_prefix} Failed to open the custom game.")
