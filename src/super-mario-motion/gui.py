import sys
import tkinter as tk
from pathlib import Path

from PIL import ImageTk, Image

# Width and Height
window_width = 650
window_height = 700

webcam_image_width = 612
webcam_image_height = 408

# Colors
color_background = '#202326'
color_foreground = '#141618'
color_white = '#FFFFFF'

# Filepaths for images that are being used on init
path_data_folder = Path(__file__).parent / "data"
path_image_webcam_sample = path_data_folder / 'webcam_sample.jpg'
path_image_pose_default = path_data_folder / 'standing.png'

# Paddings
default_image_top_padding = 50
x_padding = 20


# Function gets called once in main.py once the program starts
def init():
    global window
    window = tk.Tk()

    window.title('Super Mario Motion')
    window.minsize(window_width, window_height)
    window.maxsize(window_width, window_height)

    window.configure(background=color_background)

    # Loading default images
    try:
        image_webcam_sample = ImageTk.PhotoImage(
            Image.open(path_image_webcam_sample).resize((webcam_image_width, webcam_image_height), Image.LANCZOS))
        image_pose = ImageTk.PhotoImage(Image.open(path_image_pose_default).resize((100, 100), Image.LANCZOS))
    except FileNotFoundError:
        print("Error: File not found")
        sys.exit(1)

    # Label displaying Webcam Preview
    global label_webcam
    label_webcam = tk.Label(
        window,
        image=image_webcam_sample,
        bd=0)
    label_webcam.image = image_webcam_sample
    label_webcam.pack(pady=default_image_top_padding)

    # Frame containing UI Elements located on the bottom left
    global skeleton_active

    skeleton_active = tk.IntVar()

    frame_bottom_left = tk.Frame(
        window,
        bg=color_foreground)

    frame_bottom_left.pack(
        side='left',
        padx=x_padding
    )

    checkbox_toggle_skeleton = tk.Checkbutton(
        frame_bottom_left,
        text='Enable Skeleton',
        bg=color_foreground,
        fg=color_white,
        selectcolor=color_background,
        highlightthickness=0,
        bd=0,
        variable=skeleton_active,
        onvalue=1,
        offvalue=0,
        width=20,
        height=2)
    checkbox_toggle_skeleton.pack(
        anchor='w')

    # Debug Checkbox
    global allow_debug_info
    allow_debug_info = tk.IntVar()

    checkbox_debug_info = tk.Checkbutton(
        frame_bottom_left,
        text='Debug Info',
        bg=color_foreground,
        fg=color_white,
        selectcolor=color_background,
        highlightthickness=0,
        bd=0,
        variable=allow_debug_info,
        onvalue=1,
        offvalue=0,
        width=20,
        height=2)

    checkbox_debug_info.pack(
        anchor='w', )

    # Send Inputs Checkbox
    global send_keystrokes
    send_keystrokes = tk.IntVar()

    checkbox_toggle_inputs = tk.Checkbutton(
        frame_bottom_left,
        text='Send Inputs',
        bg=color_foreground,
        fg=color_white,
        selectcolor=color_background,
        highlightthickness=0,
        bd=0,
        variable=send_keystrokes,
        onvalue=1,
        offvalue=0,
        width=20,
        height=2)

    checkbox_toggle_inputs.pack(
        anchor='w', )

    # Text Label "Mode:"
    label_mode = tk.Label(
        frame_bottom_left,
        text = "Mode:")
    label_mode.pack(side=tk.LEFT)

    # Mode Option Menu
    list_modes = ["Simple", "Full-body"]

    global selected_mode
    selected_mode = tk.StringVar()
    selected_mode.set("Simple")

    option_menu_mode = tk.OptionMenu(
        frame_bottom_left,
        selected_mode,
        *list_modes
        )

    option_menu_mode.pack(side=tk.RIGHT)

    # Label designated for displaying the current pose
    global label_pose_visualizer
    label_pose_visualizer = tk.Label(
        window,
        image=image_pose,
        bd=0)
    label_pose_visualizer.image = image_pose
    label_pose_visualizer.pack(
        side='right',
        padx=x_padding)
    print(Path(__file__).name + " initialized")


# set_webcam_image and set_pose_image are supposed to be called in the update-loop in main.py
def set_webcam_image(array):
    array = array[:, ::-1, :]   # flip the camera horizontally only for the user
    image = ImageTk.PhotoImage(Image.fromarray(array).resize((webcam_image_width, webcam_image_height), Image.LANCZOS))
    label_webcam.config(image=image)
    label_webcam.image = image


def set_pose_image(pose):
    valid_poses = ["standing", "jumping", "crouching", "throwing", "walking_right", "walking_left", "running_right",
                   "running_left"]
    if pose in valid_poses:
        try:
            window.image_pose = ImageTk.PhotoImage(
                Image.open(path_data_folder / (pose + '.png')).resize((100, 100), Image.LANCZOS))
        except FileNotFoundError:
            print("Error: File not found")
            sys.exit(1)

        label_pose_visualizer.config(image=window.image_pose)
        label_pose_visualizer.image = window.image_pose
    else:
        print("Invalid pose")


# get_boolean_send_keystrokes and get_boolean_skeleton_active return the integer representation of their respective variable
def get_boolean_send_keystrokes():
    return send_keystrokes.get()


def get_boolean_skeleton_active():
    return skeleton_active.get()

def get_active_mode():
    return selected_mode.get()
