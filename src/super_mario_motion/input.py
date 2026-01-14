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
from pynput.keyboard import Key, KeyCode

from super_mario_motion.settings import Settings
from super_mario_motion.state import StateManager

module_prefix = "[Input]"
keyboard = None
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
        "run_throw": "shift",
        "left": "left",
        "right": "right",
        "down": "down",
        },
    "Custom": {}
    }
alphabet_len = 26

SPECIAL_KEYS = {
    "shift": Key.shift,
    "shift_l": Key.shift_l,
    "shift_r": Key.shift_r,
    "ctrl": Key.ctrl,
    "ctrl_l": Key.ctrl_l,
    "ctrl_r": Key.ctrl_r,
    "alt": Key.alt,
    "alt_l": Key.alt_l,
    "alt_r": Key.alt_r,
    "alt_gr": Key.alt_gr,
    "cmd": Key.cmd,
    "command": Key.cmd,
    "win": Key.cmd,
    "space": Key.space,
    "enter": Key.enter,
    "return": Key.enter,
    "tab": Key.tab,
    "esc": Key.esc,
    "escape": Key.esc,
    "backspace": Key.backspace,
    "delete": Key.delete,
    "home": Key.home,
    "end": Key.end,
    "page_up": Key.page_up,
    "page_down": Key.page_down,
    "left": Key.left,
    "right": Key.right,
    "up": Key.up,
    "down": Key.down,
    "caps_lock": Key.caps_lock,
    }

for i in range(1, 13):
    SPECIAL_KEYS[f"f{i}"] = getattr(Key, f"f{i}")

mapping = None

# Set initial values
send_permission = False
previous_send_permission = False
last_pose = "standing"
pose = "standing"

currently_held_keys = []
last_orientation = "right"

# Swimming repeat press configuration
last_swim_press_time = 0.0
PDI_LETTER_MAP = {}
MAPVK_VSC_TO_VK_EX = 3


def check_accessibility_permissions():
    """Prüft Berechtigungen und erzwingt ggf. den macOS-System-Dialog."""
    if sys.platform == 'darwin':  # Nur für macOS
        try:
            from ApplicationServices import AXIsProcessTrustedWithOptions, \
                kAXTrustedCheckOptionPrompt
            # Die Option kAXTrustedCheckOptionPrompt: True löst den System-Dialog aus
            options = {kAXTrustedCheckOptionPrompt: True}
            trusted = AXIsProcessTrustedWithOptions(options)
            if not trusted:
                print("[Input] Bedienungshilfen sind NICHT freigegeben.")
                print(
                    "[Input] Bitte im soeben geöffneten macOS-Dialog erlauben und das Programm neu starten.")
                # Wir geben dem User Zeit, den Dialog zu sehen, bevor wir beenden
                time.sleep(2)
                return False
            return True
        except Exception:
            print(
                "[Input] 'pyobjc-framework-ApplicationServices' fehlt. Bitte mit pip installieren.")
            return False
    return True

def get_current_key_mapping():
    scheme = state_manager.get_control_scheme()
    if scheme == "Custom":
        custom = state_manager.get_custom_key_mapping()
        if custom:
            return custom
    return CONTROL_SCHEMES.get(scheme, CONTROL_SCHEMES["Original (RetroArch)"])


def init():
    global PDI_LETTER_MAP
    if not check_accessibility_permissions():
        sys.exit(1)

    # Load the scheme of the config (needed before macOS mapping so Custom is included)
    load_custom_keymap()

    thread = threading.Thread(target=input_loop, daemon=True)
    thread.start()


def input_loop():
    """Continuously read pose/state and send corresponding key events.

    Logic:
      * Read current pose (simple or full-body depending on mode).
      * Read send_permission from StateManager.
      * On send_permission rising edge: send input for current pose.
      * On pose change while permission is active: release previous keys,
        send input for the new pose.
      * On send_permission falling edge: release all currently held keys.
    """
    global pose, last_pose, mapping, send_permission, \
        previous_send_permission, last_swim_press_time, keyboard
    check_accessibility_permissions()

    if keyboard is None:
        try:
            from pynput.keyboard import Controller
            keyboard = Controller()
            print(f"{module_prefix} Controller erfolgreich geladen.")
        except Exception as e:
            print(f"{module_prefix} Fehler bei Controller-Initialisierung: {e}")
            return

    print(Path(__file__).name + " initialized")
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
                if now - last_swim_press_time >= Settings.swim_interval:
                    press_designated_input("swimming")
                    last_swim_press_time = now
        elif previous_send_permission:
            # When send_permission just changed from True to False
            release_held_keys()
            previous_send_permission = False

        time.sleep(0.02)


def _key_down(key: str):
    """
    Drückt eine Taste.
    key:
      - einzelnes Zeichen: 'a', '1', '+', 'ä', 'Y'
      - Sondertaste: 'shift', 'left', 'enter', 'f5', ...
    """
    if not isinstance(key, str) or not key:
        return

    k = key.lower()

    # Sondertaste
    if k in SPECIAL_KEYS:
        keyboard.press(SPECIAL_KEYS[k])
        return

    # Einzelnes Zeichen (layout-aware!)
    if len(key) == 1:
        keyboard.press(KeyCode.from_char(key))
        return

    raise ValueError(f"Unbekannte Taste: {key}")


def _key_up(key: str):
    """
    Lässt eine Taste los.
    """
    if not isinstance(key, str) or not key:
        return

    k = key.lower()

    if k in SPECIAL_KEYS:
        keyboard.release(SPECIAL_KEYS[k])
        return

    if len(key) == 1:
        keyboard.release(KeyCode.from_char(key))
        return

    raise ValueError(f"Unbekannte Taste: {key}")


def press_designated_input(pose_):
    """Send key presses according to the given pose label.

    This function both triggers momentary actions (jump, throw) and sets
    up continuous key holds (walking/running/crouching), which are
    tracked in `currently_held_keys`.

    Args:
        pose_: Pose label (e.g. "walking_right", "jumping").
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


def load_custom_keymap():
    global CONTROL_SCHEMES
    config_file = state_manager.get_config_path()
    try:
        extracted_mapping = json.loads(
            Path(config_file).read_text()
            )["custom_key_mapping"]
        CONTROL_SCHEMES["Custom"] = extracted_mapping
        print(f"{module_prefix} loaded scheme from config.")
    except Exception as e:
        print(
            f"{module_prefix} Failed reading config: {e}.\n"
            f"{module_prefix} using RetroArch mapping as fallback"
            f" for custom."
            )
        CONTROL_SCHEMES["Custom"] = CONTROL_SCHEMES["Original (RetroArch)"]
