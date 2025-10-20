import pyautogui
from pathlib import Path

last_pose = "standing" #Initial position is standing
mapping ={
    "walking_right": "right",
    "standing": ""
}

def executeKeystroke(pose):
    global last_pose, mapping
    if last_pose != pose:
        pyautogui.keyUp(mapping[last_pose])
        last_pose = pose
        pyautogui.keyDown(mapping[pose])
