import tkinter as tk
from PIL import ImageTk, Image
from pathlib import Path

window_width = 650
window_height = 700

webcam_image_width = 612
webcam_image_height = 408

color_background = '#202326'
color_foreground = '#141618'
color_white = '#FFFFFF'

# TODO: Throw exception if file not found
path_data_folder = Path(__file__).parent / "data"
path_image_webcam_sample = path_data_folder / 'webcam_sample.jpg'
path_image_walking = path_data_folder / 'walking.png'

default_image_top_padding = 50
checkbox_left_padding = 20

def init():
    global window     
    window = tk.Tk()

    window.title('Super Mario Motion')
    window.minsize(window_width, window_height)
    window.maxsize(window_width, window_height)

    window.configure(background=color_background)

    image_webcam_sample = ImageTk.PhotoImage(Image.open(path_image_webcam_sample).resize((webcam_image_width,webcam_image_height), Image.LANCZOS))
    image_walking = ImageTk.PhotoImage(Image.open(path_image_walking).resize((100,100), Image.LANCZOS))

    label_webcam = tk.Label(window, image = image_webcam_sample)
    label_webcam.image = image_webcam_sample
    label_webcam.pack(pady = default_image_top_padding)

    global skeleton_active
    skeleton_active = tk.IntVar()
    global send_keystrokes
    send_keystrokes = tk.IntVar()

    checkbox_toggle_skeleton = tk.Checkbutton(
        window,
        text='Enable Skeleton',
        bg = color_foreground,
        fg = color_white,
        selectcolor=color_background,
        highlightthickness = 0,
        bd = 0,
        variable=skeleton_active,
        onvalue=1,
        offvalue=0,
        width=20)
    checkbox_toggle_skeleton.pack(anchor='w', padx= checkbox_left_padding)

    checkbox_toggle_inputs = tk.Checkbutton(
        window,
        text='Send Inputs',
        bg = color_foreground,
        fg = color_white,
        selectcolor=color_background,
        highlightthickness = 0,
        bd = 0,
        variable=send_keystrokes,
        onvalue=1,
        offvalue=0,
        width=20)
    checkbox_toggle_inputs.pack(anchor='w', padx= checkbox_left_padding)


    label_pose_visualizer = tk.Label(window, image=image_walking)
    label_pose_visualizer.image = image_walking
    label_pose_visualizer.pack()
    
    print(ImageTk.PhotoImage(Image.open(path_image_webcam_sample)).height(), ImageTk.PhotoImage(Image.open(path_image_webcam_sample)).width())

    print(Path(__file__).name + " initialized")

def update_label_webcam(new_image):
    image = ImageTk.PhotoImage(new_image.resize((300,400), Image.LANCZOS))
    window.label_webcam = tk.Label(window, image = image)

def update_label_pose_visualizer():
    print("update_label_pose_visualizer")