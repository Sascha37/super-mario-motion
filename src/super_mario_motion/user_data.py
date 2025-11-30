import platform
import os, sys
from super_mario_motion.state import StateManager

def init():
    module_prefix="[Data]"
    state_manager = StateManager()

    # Checks the OS of the User
    user_os=(platform.system().lower())
    print(f"{module_prefix} Using {user_os} operating system.")

    # Get path to the data folder relative to os
    def get_data_path(platform):
        match platform:
            case "win32":
                return os.path.join(os.getenv("APPDATA"), "SuperMarioMotion")
            case "darwin":
                return os.path.expanduser("~/Library/Application Support/SuperMarioMotion")
            case "linux":
                return os.path.expanduser("~/.local/supermariomotion")
            case _:
                raise Exception(f"{module_prefix} using unsupported OS: {platform}")

    data_path = get_data_path(user_os)
    print(f"{module_prefix} Searching for default path: {data_path}")

    # Checks if local directory exists
    if (os.path.isdir(data_path)):
        print(f"{module_prefix} Found path")
    else:
        print(f"{module_prefix} Could not find supermariomotion directory. Creating now.")
        try:
            os.makedirs(data_path)
        except:
            print(f"{module_prefix} Failed to create folder. Exiting program.")
            sys.exit(1)
        print(f"{module_prefix} Created folder {data_path}")

    # Set path in gobal state
    state_manager.set_data_folder_path(data_path)
