import pyautogui
from pathlib import Path
import threading
import time

# Set initial values
send_permission = False
previous_send_permission = False 
last_pose = "standing"
pose = "standing"

currently_held_keys = []
last_orientation = "right"

def init():
    thread = threading.Thread(target=input_loop,daemon=True)
    thread.start()

def input_loop():
    print(Path(__file__).name + " initialized")
    global pose, last_pose, mapping, send_permission, previous_send_permission
    while(True):
        if send_permission:
            if previous_send_permission == False: # When send_permission just changed from False to True
                press_designated_input(pose)
                last_pose = pose
                previous_send_permission = True
            if (last_pose != pose):
                release_held_keys()
                last_pose = pose
                press_designated_input(pose)
        elif previous_send_permission: #When send_permission just changed from True to False
            release_held_keys()
            previous_send_permission = False

        time.sleep(0.001)

def press_designated_input(pose):
    global currently_held_keys, last_orientation
    match pose:
        case "standing":
            if last_pose == "walking_left" or "walking_right" or "running_left" or "running_right":
                countersteer = "left" if last_orientation == "right" else "right"
                pyautogui.keyDown(countersteer)
                pyautogui.keyUp(countersteer)
                print("countersteer against direction: " + last_orientation)
        case "jumping":
            pyautogui.keyDown("x")
            pyautogui.keyDown(last_orientation)
            time.sleep(0.1)
            pyautogui.keyUp(last_orientation)
            pyautogui.keyUp("x")
        case "running_right":
            pyautogui.keyDown("y")
            pyautogui.keyDown("right")
            currently_held_keys.append("y")
            currently_held_keys.append("right")
            last_orientation = "right"
        case "running_left":
            pyautogui.keyDown("y")
            pyautogui.keyDown("left")
            currently_held_keys.append("y")
            currently_held_keys.append("left")
            last_orientation = "left"
        case "walking_right":
            pyautogui.keyDown("right")
            currently_held_keys.append("right")
            last_orientation = "right"
        case "walking_left":
            pyautogui.keyDown("left")
            currently_held_keys.append("left")
            last_orientation = "left"
        case "crouching":
            pyautogui.keyDown("down")
            currently_held_keys.append("down")


def release_held_keys():
    global currently_held_keys
    for key in currently_held_keys:
        pyautogui.keyUp(key)
    currently_held_keys = []

def update_pose(new_pose):
    global pose
    pose = new_pose

def update_send_permission(new_send_permission):
    global send_permission
    send_permission = new_send_permission
