import subprocess
from pathlib import Path
from sys import platform

exe, core = None, None

module_log_prefix = "[Launcher]"

config_retroarch_path = (
    "/mnt/files/SteamLibrary/steamapps/common/RetroArch/"
    )

config_rom_path = (
    f"/mnt/files/roms/nes/Super Mario Bros. (World).nes"
    )

retroarch_path = Path(config_retroarch_path)
rom_path = Path(config_rom_path)

all_paths_valid = True


def validate_path(path):
    """Validate that a given path exists and update the global flag.

    Prints an info message and sets `all_paths_valid = False` if the
    path does not exist.

    Args:
        path (Path): File or directory path to validate.
    """
    global all_paths_valid

    if not path.exists():
        print(
            f"{module_log_prefix} {path}, Path/File does not exist, please "
            f"edit the config."
            )
        all_paths_valid = False
    else:
        print(f"{module_log_prefix} {path}, Path/File found.")


validate_path(rom_path)
validate_path(retroarch_path)


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
    if not all_paths_valid:
        print(
            f"{module_log_prefix} Could not start the game. Invalid paths "
            f"set. Please edit the config."
            )
        return
    try:
        subprocess.run(
            get_command(platform), cwd=str(retroarch_path),
            check=True
            )
    except subprocess.CalledProcessError:
        print(f"{module_log_prefix} Failed to open the game.")
    except FileNotFoundError as e:
        print(f"{module_log_prefix} Could not find launchable file: {e}")
