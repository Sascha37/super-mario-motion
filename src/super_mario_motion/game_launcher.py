import subprocess
from pathlib import Path
from sys import platform

exe, core = None, None

module_log_prefix = "[Launcher]"

config_retroarch_path = ("/Users/timobarton/Library/Application "
                         "Support/Steam/steamapps/common/RetroArch")
config_rom_path = (f"/Users/timobarton/Library/Application "
                   f"Support/Steam/steamapps/common/RetroArch/downloads/Super Mario Bros. ("
                   f"World).nes")

retroarch_path = Path(config_retroarch_path)
rom_path = Path(config_rom_path)

all_paths_valid = True


def validate_path(path):
    global all_paths_valid

    if not path.exists():
        print(f"{module_log_prefix} {path}, Path/File does not exist, please edit the config.")
        all_paths_valid = False
    else:
        print(f"{module_log_prefix} {path}, Path/File found.")


validate_path(rom_path)
validate_path(retroarch_path)


def get_command(platform_):
    global exe, core
    match platform_:
        case "linux":
            exe = retroarch_path / "retroarch.sh"
            core = retroarch_path / "cores" / "fceumm_libretro.so"
        case "darwin":
            exe = retroarch_path / "RetroArch.app" / "Contents" / "MacOS" / "RetroArch"
            core = retroarch_path / "cores" / "fceumm_libretro.dylib"
        case "win32":
            exe = retroarch_path / "retroarch.exe"
            core = retroarch_path / "cores" / "fceumm_libretro.dll"
        case _:
            raise ValueError(f"{module_log_prefix} Unknown platform: {platform_}")

    return [
        str(exe),
        "-L",
        str(core),
        str(rom_path)
        ]


def launch_game():
    if not all_paths_valid:
        print(
            f"{module_log_prefix} Could not start the game. Invalid paths set. Please edit the "
            f"config.")
        return
    try:
        subprocess.run(get_command(platform), cwd=str(retroarch_path), check=True)
    except subprocess.CalledProcessError:
        print(f"{module_log_prefix} Failed to open the game.")
    except FileNotFoundError as e:
        print(f"{module_log_prefix} Could not find launchable file: {e}")
