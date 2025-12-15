"""
Maps pose labels to keyboard inputs and sends them to the active game.

Loads control schemes (including a custom mapping from config), runs a
background loop that reads the current pose and send-permission from
StateManager, and presses/releases keys via pyautogui accordingly.
"""

import json
import sys
import threading
import time
from pathlib import Path

from super_mario_motion.state import StateManager

module_prefix = "[Input]"

state_manager = StateManager()

CONTROL_SCHEMES = {
    "Original (RetroArch)": {
        "jump": "x",
        "run_throw": "y",
        "left": "left",
        "right": "right",
        "down": "down",
        },
    "supermarioplay (Web)": {
        "jump": "up",
        "run_throw": "ctrl",
        "left": "left",
        "right": "right",
        "down": "down",
        },
    "Custom": {}
    }

if sys.platform == 'win32':
    import pydirectinput as pyautogui
else:
    import pyautogui

mapping = None

# Set initial values
send_permission = False
previous_send_permission = False
last_pose = "standing"
pose = "standing"

currently_held_keys = []
last_orientation = "right"


def get_current_key_mapping():
    scheme = state_manager.get_control_scheme()
    if scheme == "Custom":
        custom = state_manager.get_custom_key_mapping()
        if custom:
            return custom
    return CONTROL_SCHEMES.get(scheme, CONTROL_SCHEMES["Original (RetroArch)"])


def init():
    global CONTROL_SCHEMES
    # Load the scheme of the config
    config_file = state_manager.get_config_path()
    try:
        extracted_mapping = json.loads(
            Path(config_file).read_text()
            )["custom_key_mapping"]
        CONTROL_SCHEMES["Custom"] = extracted_mapping
        print(f"{module_prefix} loaded scheme from config.")
    except Exception as e:
        print(f"{module_prefix} Failed reading config: {e}.")

    thread = threading.Thread(target=input_loop, daemon=True)
    thread.start()


def input_loop():
    """Continuously read pose/state and send corresponding key events.

    Logic:
      * Read current pose (simple or full-body depending on mode).
      * Read send_permission from StateManager.
      * On send_permission rising edge: send input for current pose.
      * On pose change while permission is active: release previous keys,
        send input for new pose.
      * On send_permission falling edge: release all currently held keys.
    """
    print(Path(__file__).name + " initialized")
    global pose, last_pose, mapping, send_permission, previous_send_permission
    while True:
        pose = state_manager.get_pose_full_body() if (
                state_manager.get_current_mode() ==
                "Full-body") else state_manager.get_pose()
        send_permission = state_manager.get_send_permission()
        if send_permission:
            if not previous_send_permission:
                # When send_permission just changed from False to True
                press_designated_input(pose)
                last_pose = pose
                previous_send_permission = True
            if last_pose != pose:
                release_held_keys()
                last_pose = pose
                press_designated_input(pose)
        elif previous_send_permission:
            # When send_permission just changed from True to False
            release_held_keys()
            previous_send_permission = False

        time.sleep(0.02)


def _translate_key_for_windows_layout(key: str) -> str:
    """Layout-abhängige Übersetzung für Windows (automatisch per aktivem Layout).

    Hintergrund: pydirectinput sendet effektiv US-Scancodes. Um auf Windows
    unabhängig vom aktiven Tastaturlayout (QWERTY/QWERTZ/AZERTY/…) den
    gewünschten Buchstaben zu erzeugen, ermitteln wir per Windows-API (HKL +
    VkKeyScanExW) den zugehörigen Virtual-Key (VK_A..VK_Z) für den Ziel-
    buchstaben und leiten daraus den pydirectinput-Key (a..z) ab.

    - Nur auf Windows aktiv.
    - Nur für einfache Buchstaben a–z; andere Tasten (Pfeile, Ctrl, …) bleiben
      unverändert.
    - Fallback bei Fehlern: unverändert zurückgeben.
    """
    if sys.platform != 'win32':
        return key

    # Nur einfache Buchstaben übersetzen (pydirectinput-Keynamen sind lower-case)
    if not (isinstance(key, str) and len(key) == 1 and key.isalpha()):
        return key

    try:
        # Lazy-import, nur wenn wirklich auf Windows ausgeführt
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL('user32', use_last_error=True)

        user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
        user32.GetKeyboardLayout.restype = wintypes.HANDLE  # HKL

        user32.VkKeyScanExW.argtypes = [wintypes.WCHAR, wintypes.HANDLE]
        user32.VkKeyScanExW.restype = wintypes.SHORT

        hkl = user32.GetKeyboardLayout(0)
        if not hkl:
            return key

        ch = key.lower()
        res = user32.VkKeyScanExW(ch, hkl)
        if res == -1:
            return key

        vk_code = res & 0xFF

        VK_A = 0x41
        VK_Z = 0x5A
        if VK_A <= vk_code <= VK_Z:
            return chr(ord('a') + (vk_code - VK_A))
        return key
    except Exception:
        return key


def _key_down(key: str):
    pyautogui.keyDown(_translate_key_for_windows_layout(key))


def _key_up(key: str):
    pyautogui.keyUp(_translate_key_for_windows_layout(key))


def press_designated_input(pose_):
    """Send key presses according to the given pose label.

    This function both triggers momentary actions (jump, throw) and sets
    up continuous key holds (walking/running/crouching), which are
    tracked in `currently_held_keys`.

    Args:
        pose_: Pose label (e.g. 'walking_right', 'jumping').
    """
    global currently_held_keys, last_orientation

    mapping_ = get_current_key_mapping()
    jump = mapping_["jump"]
    run_throw = mapping_["run_throw"]
    left = mapping_["left"]
    right = mapping_["right"]
    down = mapping_["down"]

    match pose_:
        case "standing":
            pass
        case "jumping":
            _key_down(jump)
            _key_down(last_orientation)
            time.sleep(0.1)
            _key_up(last_orientation)
            _key_up(jump)
        case "running_right":
            _key_down(run_throw)
            _key_down(right)
            currently_held_keys.append(run_throw)
            currently_held_keys.append(right)
            last_orientation = right
        case "running_left":
            _key_down(run_throw)
            _key_down(left)
            currently_held_keys.append(run_throw)
            currently_held_keys.append(left)
            last_orientation = left
        case "walking_right":
            _key_down(right)
            currently_held_keys.append(right)
            last_orientation = right
        case "walking_left":
            _key_down(left)
            currently_held_keys.append(left)
            last_orientation = left
        case "crouching":
            _key_down(down)
            currently_held_keys.append(down)
        case "throwing":
            _key_down(run_throw)
            _key_up(run_throw)
        case "swimming":
            _key_down(last_orientation)
            _key_down(jump)
            time.sleep(0.05)
            _key_up(last_orientation)
            _key_up(jump)

        case _:
            print(f"{module_prefix} No input defined for: " + pose_)


def release_held_keys():
    global currently_held_keys
    for key in currently_held_keys:
        _key_up(key)
    currently_held_keys = []
