import gui
import vision
import vision_ml
import input
from state import StateManager

# Function gets called every millisecond after the mainloop of the tkinter ui
def update():

    # Retrieve Checkbox Info from gui.py
    send_keystrokes_checkbox = gui.get_boolean_send_keystrokes()

    # Retrieve predicted pose from vision.py
    current_pose = vision.get_current_pose()

    # Update Images to display in gui.py
    vision.update_images()
    gui.set_webcam_image(*state_manager.get_all_opencv_images())

    # Update Pose Preview Indicator in gui.py
    gui.update_pose(current_pose)
    gui.update_pose_image()
    gui.update_pose_text()
    gui.update_debug_landmarks(state_manager.get_landmark_string())

    # Update Pose and update_send_permission in input.py
    input.update_pose(current_pose)
    input.update_send_permission(send_keystrokes_checkbox)



    gui.window.after(1, update)


if __name__ == '__main__':
    print("Super Mario Motion started")
    state_manager = StateManager()
    state_manager.set_pose("newwallo")
    print(state_manager.get_pose())#TODO: Remove Debug
    vision.init()
    vision_ml.init()
    input.init()
    gui.init()

    gui.window.after(0, update)
    gui.window.mainloop()
