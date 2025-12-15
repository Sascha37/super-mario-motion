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

# Swimming repeat press configuration
swim_repeat_interval = 0.25  # seconds between swim button taps while pose is held
last_swim_press_time = 0.0
PDI_LETTER_MAP = {}


def get_current_key_mapping():
    scheme = state_manager.get_control_scheme()
    if scheme == "Custom":
        custom = state_manager.get_custom_key_mapping()
        if custom:
            return custom
    return CONTROL_SCHEMES.get(scheme, CONTROL_SCHEMES["Original (RetroArch)"])


def init():
    global CONTROL_SCHEMES, PDI_LETTER_MAP

    if sys.platform == "win32":
        try:
            PDI_LETTER_MAP = build_pydirectinput_letter_map()
            print(f"{module_prefix} pydirectinput letter map loaded ({len(PDI_LETTER_MAP)}/26).")
        except Exception as e:
            print(f"{module_prefix} Failed building pydirectinput letter map: {e}.")
            PDI_LETTER_MAP = {}

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
    global pose, last_pose, mapping, send_permission, previous_send_permission, last_swim_press_time
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
                # Reset swim timer when starting to send
                last_swim_press_time = time.time()
            if last_pose != pose:
                release_held_keys()
                last_pose = pose
                press_designated_input(pose)
                # Reset swim timer on pose change
                if pose == "swimming":
                    last_swim_press_time = time.time()
            # While holding a swimming pose, repeatedly tap the swim button
            if pose == "swimming":
                now = time.time()
                if now - last_swim_press_time >= swim_repeat_interval:
                    press_designated_input("swimming")
                    last_swim_press_time = now
        elif previous_send_permission:
            # When send_permission just changed from True to False
            release_held_keys()
            previous_send_permission = False

        time.sleep(0.02)



def _key_down(key: str):
    if sys.platform == "win32" and isinstance(key, str) and len(key) == 1 and key.isalpha():
        k = key.lower()
        mapped = PDI_LETTER_MAP.get(k)
        if mapped:
            pyautogui.keyDown(mapped)
            return
    pyautogui.keyDown(key)


def _key_up(key: str):
    if sys.platform == "win32" and isinstance(key, str) and len(key) == 1 and key.isalpha():
        k = key.lower()
        mapped = PDI_LETTER_MAP.get(k)
        if mapped:
            pyautogui.keyUp(mapped)
            return
    pyautogui.keyUp(key)



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

def build_pydirectinput_letter_map():
    """
    Map intended a–z to the pydirectinput key name (physical US key) that
    produces it on the active Windows layout.
    """
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.WinDLL("user32", use_last_error=True)

    user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]
    user32.GetKeyboardLayout.restype = wintypes.HANDLE

    user32.MapVirtualKeyExW.argtypes = [wintypes.UINT, wintypes.UINT, wintypes.HANDLE]
    user32.MapVirtualKeyExW.restype = wintypes.UINT

    user32.ToUnicodeEx.argtypes = [
        wintypes.UINT, wintypes.UINT,
        ctypes.POINTER(ctypes.c_ubyte),
        wintypes.LPWSTR, ctypes.c_int,
        wintypes.UINT, wintypes.HANDLE
    ]
    user32.ToUnicodeEx.restype = ctypes.c_int

    # Set-1 scancodes for physical A–Z keys (US positions)
    SC = {
        "a": 0x1E, "b": 0x30, "c": 0x2E, "d": 0x20, "e": 0x12, "f": 0x21,
        "g": 0x22, "h": 0x23, "i": 0x17, "j": 0x24, "k": 0x25, "l": 0x26,
        "m": 0x32, "n": 0x31, "o": 0x18, "p": 0x19, "q": 0x10, "r": 0x13,
        "s": 0x1F, "t": 0x14, "u": 0x16, "v": 0x2F, "w": 0x11, "x": 0x2D,
        "y": 0x15, "z": 0x2C,
    }

    hkl = user32.GetKeyboardLayout(0)
    if not hkl:
        return {}

    MAPVK_VSC_TO_VK_EX = 3
    buf = ctypes.create_unicode_buffer(8)
    out = {}  # produced_char -> physical_key_name

    def produced_char(scancode: int) -> str | None:
        vk = user32.MapVirtualKeyExW(scancode, MAPVK_VSC_TO_VK_EX, hkl)
        if not vk:
            return None

        state = (ctypes.c_ubyte * 256)()  # no modifiers
        buf.value = ""

        rc = user32.ToUnicodeEx(vk, scancode, state, buf, len(buf), 0, hkl)

        # dead key / no translation
        if rc <= 0:
            return None

        return buf.value[0].lower()

    for physical_key, sc in SC.items():
        ch = produced_char(sc)
        if ch and "a" <= ch <= "z" and ch not in out:
            out[ch] = physical_key

        if len(out) == 26:
            break

    return out

