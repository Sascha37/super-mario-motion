import sys
import threading
import time
from pathlib import Path

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
    }

from .state import StateManager

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

state_manager = StateManager()


def get_current_key_mapping():
    scheme = state_manager.get_control_scheme()
    if scheme == "Custom":
        custom = state_manager.get_custom_key_mapping()
        if custom:
            return custom
    return CONTROL_SCHEMES.get(scheme, CONTROL_SCHEMES["Original (RetroArch)"])


def init():
    thread = threading.Thread(target=input_loop, daemon=True)
    thread.start()


def input_loop():
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


def press_designated_input(pose_):
    global currently_held_keys, last_orientation

    mapping = get_current_key_mapping()
    jump = mapping["jump"]
    run_throw = mapping["run_throw"]
    left = mapping["left"]
    right = mapping["right"]
    down = mapping["down"]

    match pose_:
        case "standing":
            pass
        case "jumping":
            pyautogui.keyDown(jump)
            pyautogui.keyDown(last_orientation)
            time.sleep(0.1)
            pyautogui.keyUp(last_orientation)
            pyautogui.keyUp(jump)
        case "running_right":
            pyautogui.keyDown(run_throw)
            pyautogui.keyDown(right)
            currently_held_keys.append(run_throw)
            currently_held_keys.append(right)
            last_orientation = right
        case "running_left":
            pyautogui.keyDown(run_throw)
            pyautogui.keyDown(left)
            currently_held_keys.append(run_throw)
            currently_held_keys.append(left)
            last_orientation = left
        case "walking_right":
            pyautogui.keyDown(right)
            currently_held_keys.append(right)
            last_orientation = right
        case "walking_left":
            pyautogui.keyDown(left)
            currently_held_keys.append(left)
            last_orientation = left
        case "crouching":
            pyautogui.keyDown(down)
            currently_held_keys.append(down)
        case "throwing":
            pyautogui.keyDown(run_throw)
            pyautogui.keyUp(run_throw)
        case _:
            print("Input: No input defined for: " + pose_)


def release_held_keys():
    global currently_held_keys
    for key in currently_held_keys:
        pyautogui.keyUp(key)
    currently_held_keys = []
