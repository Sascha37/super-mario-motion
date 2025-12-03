"""
Initialize and manage Super Mario Motion user data and configuration.

Creates a platform-specific data directory, ensures a config subfolder
and config.json exist (writing defaults if needed), and stores the data
and config paths in the global StateManager.
"""

import os
import platform
import sys
import json

from super_mario_motion.state import StateManager


module_prefix = "[Data]"

default_config = {
    "emu-path": "null",
    "rom-path": "null",
    "custom-game-path": "null",

    "custom_key_mapping": {
        "jump": "space",
        "run_throw": "shift",
        "left": "a",
        "right": "d",
        "down": "s"
    }
}

state_manager = StateManager()

def init():
    # Checks the OS of the User
    user_os = (platform.system().lower())
    print(f"{module_prefix} Using {user_os} operating system.")

    # Get path to the data folder relative to os
    def get_data_path(platform_):
        match platform_:
            case "windows":
                return os.path.join(os.getenv("APPDATA"), "SuperMarioMotion")
            case "darwin":
                return os.path.expanduser(
                    "~/Library/Application Support/SuperMarioMotion"
                    )
            case "linux":
                return os.path.expanduser("~/.local/share/supermariomotion")
            case _:
                raise Exception(
                    f"{module_prefix} using unsupported OS: {platform_}"
                    )

    data_path = get_data_path(user_os)
    print(f"{module_prefix} Searching for default path: {data_path}")

    # Checks if local directory exists
    if os.path.isdir(data_path):
        print(f"{module_prefix} Found data path.")
    else:
        create_folder_helper(data_path)

    # Set path in global state
    state_manager.set_data_folder_path(data_path)

    # Check if config folder exists, if not create it
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
