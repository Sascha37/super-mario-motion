import gui
import vision
import vision_ml
import input

# Function gets called every millisecond after the mainloop of the tkinter ui
def update():
    image = vision.get_latest_raw_frame()
    image_with_skeleton = vision.get_latest_skeleton()
    skeleton_active_checkbox = gui.get_boolean_skeleton_active()
    send_keystrokes_checkbox = gui.get_boolean_send_keystrokes()
    current_pose = vision.get_current_pose()
    # Update Webcam Preview in GUI
    if image is not None and image_with_skeleton is not None:
        gui.set_webcam_image(image_with_skeleton if skeleton_active_checkbox else image)
    # Update Pose Preview Indicator in GUI
    gui.set_pose_image(current_pose)
    # Press the respective button associated with the pose
    input.update_pose(current_pose)
    input.update_send_permission(send_keystrokes_checkbox)

    gui.window.after(1, update)


if __name__ == '__main__':
    print("Super Mario Motion started")
    vision.init()
    vision_ml.init()
    input.init()
    gui.init()

    gui.window.after(0, update)
    gui.window.mainloop()
    vision.exitApp = True
