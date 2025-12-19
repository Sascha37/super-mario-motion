"""
Initialize and manage Super Mario Motion user data and configuration.

Creates a platform-specific data directory, ensures a config subfolder
and config.json exist (writing defaults if needed), and stores the data
and config paths in the global StateManager.
"""

import json
import os
import platform
import sys

from super_mario_motion.state import StateManager

default_emu_path, default_rom_path = "null", "null"

module_prefix = "[Data]"

default_config = "null"

state_manager = StateManager()


def init():
    # Checks the OS of the User
    global default_config, default_emu_path, default_rom_path
    user_os = (platform.system().lower())
    print(f"{module_prefix} Using {user_os} operating system.")

    # Get the path to the data folder relative to os
    def get_data_path(platform_):
        global default_emu_path, default_rom_path
        match platform_:
            case "windows":
                default_emu_path = (r"C:\Program Files ("
                                    r"x86)\SteamLibrary\steamapps\common"
                                    r"\RetroArch")
                default_rom_path = (r"C:\Program Files ("
                                    r"x86)\SteamLibrary\steamapps\common"
                                    r"\RetroArch\downloads\Super Mario Bros. "
                                    r"(World).nes")
                return os.path.join(os.getenv("APPDATA"), "SuperMarioMotion")
            case "darwin":
                default_emu_path = os.path.expanduser(
                    "~/Library/Application "
                    "Support/Steam/steamapps/common/RetroArch"
                    )
                default_rom_path = os.path.expanduser(
                    "~/Library/Application "
                    "Support/Steam/steamapps/common/RetroArch/downloads"
                    "/Super Mario Bros. (World).nes"
                    )
                return os.path.expanduser(
                    "~/Library/Application Support/SuperMarioMotion"
                    )
            case "linux":
                default_emu_path = os.path.expanduser(
                    "~/.steam/root/steamapps/common/RetroArch"
                    )
                default_rom_path = os.path.expanduser(
                    "~/.steam/root/steamapps/common/RetroArch/downloads"
                    "/Super Mario Bros. (World).nes"
                    )
                return os.path.expanduser("~/.local/share/supermariomotion")
            case _:
                raise Exception(
                    f"{module_prefix} using unsupported OS: {platform_}"
                    )

    data_path = get_data_path(user_os)
    default_config = {
        "emu-path": f"{default_emu_path}",
        "rom-path": f"{default_rom_path}",
        "custom-game-path": "null",

        "custom_key_mapping": {
            "jump": "space",
            "run_throw": "shift",
            "left": "a",
            "right": "d",
            "down": "s"
            }
        }
    print(f"{module_prefix} Searching for default path: {data_path}")

    # Checks if the local directory exists
    if os.path.isdir(data_path):
        print(f"{module_prefix} Found data path.")
    else:
        create_folder_helper(data_path)

    # Set path in global state
    state_manager.set_data_folder_path(data_path)

    # Check if the config folder exists, if not, create it
    config_folder_path = os.path.join(data_path, "config")
    if os.path.isdir(config_folder_path):
        print(f"{module_prefix} found config folder.")
    else:
        create_folder_helper(config_folder_path)

    # Check if config.json exists within the config folder
    config_path = os.path.join(config_folder_path, "config.json")
    if os.path.isfile(config_path):
        print(f"{module_prefix} found config file.")
    else:
        with open(config_path, mode="w", encoding="utf-8") as write_file:
            json.dump(default_config, write_file, indent=4)
        print(f"{module_prefix} Config created.")
    state_manager.set_config_path(config_path)

    # Validate the loaded config
    try:
        with open(config_path, "r") as f:
            json.load(f)
            state_manager.set_invalid_config(False)
    except Exception as e:
        print(f"{module_prefix} The JSON syntax of the config file"
              f" is violated: {e}")
        state_manager.set_invalid_config(True)


def create_folder_helper(path):
    try:
        os.makedirs(path)
    except OSError as e:
        print(
            f"{module_prefix} Failed to create folder: {e}. Exiting "
            f"program."
            )
        sys.exit(1)
    print(f"{module_prefix} Created folder {path}")
