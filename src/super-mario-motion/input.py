import pyautogui
from pathlib import Path
import threading
import time

send_permission = False
previous_send_permission = False 
last_pose = "standing" #Initial position is standing
pose = "standing"


mapping ={
    "walking_right": ["right", "hold"],
    "standing": ["","hold"],
    "jumping": ["y", "prolonged_single_press"]
}

def init():
    thread = threading.Thread(target=input_loop,daemon=True)
    thread.start()

def input_loop():
    print(Path(__file__).name + " initialized")
    global pose, last_pose, mapping, send_permission, previous_send_permission
    while(True):
        if send_permission:
            if previous_send_permission == False: # When send_permission just changed from False to True
                pyautogui.keyDown(mapping[pose][0])
                last_pose = pose
                previous_send_permission = True
            if (last_pose != pose):
                pyautogui.keyUp(mapping[last_pose][0])
                last_pose = pose
                pyautogui.keyDown(mapping[pose][0])
        elif previous_send_permission: #When send_permission just changed from True to False
            pyautogui.keyUp(mapping[last_pose])
            previous_send_permission = False


        time.sleep(0.001)
    

def update_pose(new_pose):
    global pose
    pose = new_pose

def update_send_permission(new_send_permission):
    global send_permission
    send_permission = new_send_permission
