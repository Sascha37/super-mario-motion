"""
Creates the Tkinter window, webcam and pose previews, gamepad visualization,
mode selection (Simple, Full-body, Collect) and control scheme selection.
Handles automated pose-sample collection runs, help/document opening, and
launching the configured game or web version.
"""

import getpass
import os
import platform
import random
import subprocess
import sys
import threading
import tkinter as tk
import tkinter.font as tkfont
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

from super_mario_motion import game_launcher, path_helper as ph
from super_mario_motion import main as main
from super_mario_motion import vision as vision
from super_mario_motion.settings import Settings
from super_mario_motion.state import StateManager

pose = ""

array = None
window = None
frame_bottom_left, frame_bottom_right = None, None
root_frame = None
label_webcam = None
selected_preview, selected_mode, selected_control_scheme = None, None, None
allow_debug_info, send_keystrokes, checkbox_toggle_inputs = None, None, None
(
    label_virtual_gamepad_visualizer, label_pose_visualizer,
    label_current_pose,
    label_debug_landmarks
    ) = None, None, None, None
button_collect_start, label_collect_status = None, None
startup_overlay = None
startup_overlay_label = None
geometry_normal, geometry_collect, screen_width, screen_height = (
    None, None,
    None, None
    )
font_collect_normal, font_collect_large = None, None

button_launch_game, label_config_warning = None, None

# Webcam preview
webcam_image_width = 612
webcam_image_height = 408
collect_scale = 1.1

# Gamepad
gamepad_image_width = 200
gamepad_image_height = 100

# Colors
color_background = "#202326"
color_dark_widget = "#141618"
color_white = "#FFFFFF"
color_disabled_background = "#444444"
color_disabled_text = "#888888"
# Filepaths for images that are being used on init
path_image_webcam_sample = ph.resource_path(
    os.path.join("images", "webcam_sample.jpg")
    )
path_image_pose_default = ph.resource_path(
    os.path.join("images", "unknown.png")
    )
path_image_gamepad = ph.resource_path(os.path.join("images", "gamepad.png"))

# App Icons per platform
path_icon_windows = ph.resource_path(os.path.join("images", "icon.ico"))
path_icon_mac = ph.resource_path(os.path.join("images", "icon.icns"))
path_icon_linux = ph.resource_path(os.path.join("images", "icon.png"))

# Paddings
label_webcam_top_padding = 20
edge_padding_default = 20
horizontal_padding = (650 - webcam_image_width) // 2
frame_padding_y = (20, 0)

# Window size
window_width = webcam_image_width + 2 * edge_padding_default
window_height = 750

# Collecting
COLLECTION_STEPS = [
    ("standing", 10),
    ("walking_left", 10),
    ("running_left", 10),
    ("walking_right", 10),
    ("running_right", 10),
    ("jumping", 10),
    ("crouching", 10),
    ("throwing", 10),
    ("swimming", 10),
    ]
CSV_PATH = "pose_samples.csv"
current_run_csv = CSV_PATH

# Will hold the randomized order for a single collection run
collection_order = None

collecting = False
collect_stop = False
after_handles = []
previous_mode_collect = False

# StateManager
state_manager = StateManager()


# Function gets called once in main.py once the program starts
def init():
    """Initialize the main GUI window and all static widgets.

    This sets up layout, styles, default images, and registers callbacks
    for mode selection, buttons, and window close events.
    """
    global window, root_frame
    global frame_bottom_left, frame_bottom_right
    global label_webcam
    global selected_preview, selected_mode, selected_control_scheme
    global allow_debug_info, send_keystrokes, checkbox_toggle_inputs
    global label_virtual_gamepad_visualizer, label_pose_visualizer, \
        label_current_pose, \
        label_debug_landmarks
    global button_collect_start, label_collect_status
    global geometry_normal, geometry_collect, screen_width, screen_height
    global font_collect_normal, font_collect_large, window_width, window_height
    global button_launch_game

    window = tk.Tk()
    window.title("Super Mario Motion")
    window.minsize(window_width, window_height)
    window.resizable(False, False)
    window.configure(background=color_background)

    window.protocol("WM_DELETE_WINDOW", close)
    root_frame = tk.Frame(window, bg=color_background)
    root_frame.pack(expand=True)

    # always open the gui in the center of the screen
    system = platform.system()

    # Set application icon depending on the platform
    try:
        if system == "Windows":
            # Windows uses .ico directly
            window.iconbitmap(path_icon_windows)
        elif system == "Darwin":
            # macOS: use .icns via iconphoto
            icon_img = ImageTk.PhotoImage(Image.open(path_icon_mac))
            window.iconphoto(True, icon_img)
            # keep a reference to avoid garbage collection
            window._icon_img = icon_img
        else:
            # Linux / other: prefer PNG
            icon_img = ImageTk.PhotoImage(Image.open(path_icon_linux))
            window.iconphoto(True, icon_img)
            window._icon_img = icon_img
    except Exception as e:
        # Fail gracefully if the icon cannot be loaded (e.g., missing file)
        print(f"Icon load warning: {e}")

    if system in ("Windows", "Darwin"):  # calculation for Windows and macOS
        window.withdraw()
        window.update_idletasks()
        center_window(window_width, window_height)

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        geometry_normal = f"{window_width}x{window_height}+{x}+{y}"
        geometry_collect = f"{screen_width}x{screen_height}+0+0"

        window.geometry(geometry_normal)
        window.deiconify()

    if system == "Linux":
        try:
            cmd = "xrandr | grep ' connected primary' | cut -d' ' -f4"
            geometry_collect = subprocess.check_output(
                cmd, shell=True, text=True
                ).strip()
        except subprocess.CalledProcessError as e:
            print(f"[GUI] Could not get resolution on Linux {e}")
            geometry_normal = "1920x1080+0+0"

    if system == "Darwin":
        # always open the gui on top of all other windows for macOS
        window.lift()
        window.attributes("-topmost", True)
        window.after(100, lambda: window.attributes("-topmost", False))

    # Loading default images
    try:
        image_webcam_sample = ImageTk.PhotoImage(
            Image.open(path_image_webcam_sample).resize(
                (webcam_image_width, webcam_image_height),
                Image.LANCZOS
                )
            )
        image_pose = ImageTk.PhotoImage(
            Image.open(path_image_pose_default).resize(
                (100, 100),
                Image.LANCZOS
                )
            )
        image_gamepad = ImageTk.PhotoImage(
            Image.open(path_image_gamepad).resize(
                (gamepad_image_width, gamepad_image_height),
                Image.LANCZOS
                )
            )
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)

    # Image Label for the preview of the webcam
    label_webcam = tk.Label(root_frame, image=image_webcam_sample, bd=0)
    label_webcam.image = image_webcam_sample
    label_webcam.grid(
        row=0,
        column=0,
        columnspan=2,
        pady=(label_webcam_top_padding, 0),
        padx=(horizontal_padding, horizontal_padding)
        )

    # Frame Bottom Left
    frame_bottom_left = tk.Frame(root_frame, bg=color_dark_widget)
    # Widgets on these rows expand evenly
    frame_bottom_left.columnconfigure(0, weight=1)
    frame_bottom_left.columnconfigure(1, weight=1)
    frame_bottom_left.grid(
        row=1,
        column=0,
        padx=(horizontal_padding, 25),
        pady=frame_padding_y,
        sticky="ne"
        )

    buttons_frame = tk.Frame(frame_bottom_left, bg=color_dark_widget)
    buttons_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)

    # Button "Launch Game"
    button_launch_game = ttk.Button(
        buttons_frame,
        text="Launch Game",
        command=start_game_button_action,
        style="Custom.TButton"
        )

    button_launch_game.grid(
        row=0,
        column=0,
        sticky="nsew"
        )

    # Button "Help"
    button_help = ttk.Button(
        buttons_frame,
        text="Help",
        command=open_help_menu,
        style="Custom.TButton"
        )

    button_help.grid(
        row=0,
        column=1,
        sticky="nsew"
        )

    button_config = ttk.Button(
        buttons_frame,
        text="Edit Config",
        command=open_config,
        style="Custom.TButton",
        )

    button_config.grid(
        row=1,
        column=0,
        sticky="nsew"
        )

    button_config_reload = ttk.Button(
        buttons_frame,
        text="Reload Config",
        command=reload_config,
        style="Custom.TButton",
        )

    button_config_reload.grid(
        row=1,
        column=1,
        sticky="nsew"
        )

    # Separator
    spacer = tk.Frame(
        frame_bottom_left,
        height=10,
        bg=color_background
        )

    spacer.grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="ew"
        )

    # Text Label "Preview:"
    label_preview = tk.Label(
        frame_bottom_left,
        bg=color_dark_widget,
        fg=color_white,
        text="Preview:"
        )
    label_preview.grid(
        row=3,
        column=0
        )

    # Custom ttk Style for Combobox
    style = ttk.Style()
    style.theme_use("alt")
    style.configure(
        "Custom.TCombobox",
        fieldbackground=color_dark_widget,
        background=color_dark_widget,
        foreground="white"
        )
    style.map(
        "Custom.TCombobox",
        fieldbackground=[("readonly", color_dark_widget)],
        foreground=[("readonly", "white")],
        background=[("readonly", color_dark_widget)]
        )

    # Custom ttk Style for Buttons
    style.configure(
        "Custom.TButton",
        fieldbackground=color_dark_widget,
        background=color_dark_widget,
        foreground="white"
        )
    style.map(
        "Custom.TButton",
        background=[
            ("active", "white"),
            ("pressed", "white"),
            ("disabled", color_disabled_background),
            ],
        foreground=[
            ("active", "black"),
            ("pressed", "black"),
            ("disabled", color_disabled_text)
            ],
        embossed=[
            ("disabled", 0)
            ]
        )

    # Custom ttk Style for Separator
    style.configure(
        "Custom.TSeparator",
        background="black"
        )

    # This is needed to deselect the text inside of a ttk Combobox
    def clear_combobox_selection(event):
        event.widget.selection_clear()

    update_launch_button_state()

    # Preview Combobox
    global selected_preview
    selected_preview = tk.StringVar()
    option_menu_preview = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_preview,
        state="readonly",
        style="Custom.TCombobox"
        )
    option_menu_preview.bind("<<ComboboxSelected>>", clear_combobox_selection)
    option_menu_preview["values"] = [
        "Webcam", "Webcam + Skeleton",
        "Skeleton Only"
        ]
    option_menu_preview.current(0)
    option_menu_preview.grid(row=3, column=1)

    # "Mode:" Text Label
    label_mode = tk.Label(
        frame_bottom_left, bg=color_dark_widget,
        fg=color_white, text="Mode:"
        )
    label_mode.grid(row=4, column=0)

    # Webcam Combobox
    global selected_cam
    selected_cam = tk.StringVar()
    option_menu_cam = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_cam,
        state="readonly",
        style="Custom.TCombobox"
        )

    option_menu_cam.bind("<<ComboboxSelected>>", change_cam)
    option_menu_cam["values"] = main.gui_cams_available
    option_menu_cam.current(0)
    option_menu_cam.grid(row=2, column=1)

    # "Mode:" Text Label
    label_cam = tk.Label(
        frame_bottom_left, bg=color_dark_widget,
        fg=color_white, text="Cam:"
        )
    label_cam.grid(row=2, column=0)

    # Mode Combobox
    global selected_mode
    selected_mode = tk.StringVar()

    # Gets called when the Mode Combobox is selected
    def on_mode_change(event):
        event.widget.selection_clear()
        apply_mode(selected_mode.get())

    option_menu_mode = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_mode,
        state="readonly",
        style="Custom.TCombobox"
        )
    option_menu_mode.bind("<<ComboboxSelected>>", on_mode_change)
    option_menu_mode["values"] = ["Simple", "Full-body", "Collect"]
    option_menu_mode.current(0)
    option_menu_mode.grid(row=4, column=1)

    # Control Scheme Label
    global selected_control_scheme
    label_control_scheme = tk.Label(
        frame_bottom_left, bg=color_dark_widget,
        fg=color_white, text="Game:"
        )
    label_control_scheme.grid(row=5, column=0)

    # Control Scheme Combobox
    selected_control_scheme = tk.StringVar()
    option_menu_control_scheme = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_control_scheme,
        state="readonly",
        style="Custom.TCombobox"
        )

    def on_control_scheme_change(event):
        clear_combobox_selection(event)
        update_launch_button_state()

    option_menu_control_scheme.bind(
        "<<ComboboxSelected>>",
        on_control_scheme_change
        )
    option_menu_control_scheme["values"] = [
        "Supermarioplay (Web)",
        "Original (RetroArch)",
        "Custom"
        ]
    option_menu_control_scheme.current(0)
    option_menu_control_scheme.grid(row=5, column=1)

    update_launch_button_state()

    # Debug Info Checkbox
    global allow_debug_info
    allow_debug_info = tk.IntVar(value=0)
    checkbox_debug_info = tk.Checkbutton(
        frame_bottom_left, text="Debug Info",
        bg=color_dark_widget, fg=color_white,
        selectcolor=color_background,
        highlightthickness=0, bd=0,
        variable=allow_debug_info, width=20,
        height=2
        )
    checkbox_debug_info.grid(
        row=6,
        column=0,
        columnspan=2,
        sticky="ew"
        )

    # Send Inputs Checkbox
    global send_keystrokes, checkbox_toggle_inputs
    send_keystrokes = tk.IntVar()
    checkbox_toggle_inputs = tk.Checkbutton(
        frame_bottom_left,
        text="Send Inputs",
        bg=color_dark_widget,
        fg=color_white,
        selectcolor=color_background,
        highlightthickness=0,
        bd=0, variable=send_keystrokes,
        width=20, height=2
        )
    checkbox_toggle_inputs.grid(
        row=7,
        column=0,
        columnspan=2,
        sticky="ew"
        )

    # Frame bottom right
    frame_bottom_right = tk.Frame(root_frame, bg=color_dark_widget)
    frame_bottom_right.grid(
        row=1,
        column=1,
        padx=(0, horizontal_padding),
        pady=frame_padding_y,
        sticky="nw"
        )

    # gamepad
    global label_virtual_gamepad_visualizer
    label_virtual_gamepad_visualizer = tk.Label(
        frame_bottom_right,
        image=image_gamepad, bd=0
        )
    label_virtual_gamepad_visualizer.image = image_gamepad
    label_virtual_gamepad_visualizer.grid(row=0, column=0)

    # pose image
    global label_pose_visualizer
    label_pose_visualizer = tk.Label(
        frame_bottom_right, image=image_pose,
        bd=0
        )
    label_pose_visualizer.image = image_pose
    label_pose_visualizer.grid(row=0, column=1)

    # pose text
    global label_current_pose
    label_current_pose = tk.Label(
        frame_bottom_right,
        bg=color_dark_widget,
        fg=color_white,
        text="Current Pose:" + pose
        )
    label_current_pose.grid(row=1, column=0, columnspan=2)

    # debug text
    global label_debug_landmarks
    label_debug_landmarks = tk.Label(
        frame_bottom_right, bg=color_dark_widget,
        fg=color_white,
        width=60, height=10, font=("Consolas", 6)
        )
    label_debug_landmarks.grid(row=2, column=0, columnspan=2)

    config_validation()

    # Text Label for the collection status, visible during collect mode
    global label_collect_status, button_collect_start
    font_collect_normal = tkfont.Font(family="Consolas", size=25)
    font_collect_large = tkfont.Font(family="Consolas", size=58)
    label_collect_status = tk.Label(
        root_frame, bg=color_background,
        fg=color_white,
        font=font_collect_normal,
        width=23
        )
    label_collect_status.grid(row=2, column=0, columnspan=2, pady=(20, 0))
    label_collect_status.grid_remove()

    # Start Collecting ttk Button
    button_collect_start = ttk.Button(
        frame_bottom_right,
        text="Start Collecting",
        command=start_collect_sequence,
        style="Custom.TButton"
        )
    button_collect_start.grid(row=0, column=0, columnspan=2, pady=(10, 0))
    button_collect_start.grid_remove()

    if system == "Darwin":
        # Ensure the window is large enough for all widgets and center it
        # This is especially important on macOS where controls can be wider
        window.update_idletasks()
        required_w = window.winfo_reqwidth()
        required_h = window.winfo_reqheight()

        final_w = max(window_width, required_w)
        final_h = max(window_height, required_h)

        # Update globals so other functions (e.g., apply_mode) use the final
        # size
        window_width = final_w
        window_height = final_h

        # Recompute geometry_normal centered on the current screen
        sw = window.winfo_screenwidth()
        sh = window.winfo_screenheight()
        x = (sw - final_w) // 2
        y = (sh - final_h) // 2
        geometry_normal = f"{final_w}x{final_h}+{x}+{y}"

        window.geometry(geometry_normal)
        window.minsize(final_w, final_h)
        window.resizable(False, False)

    print(Path(__file__).name + " initialized")


def show_startup_overlay(message: str = "Please wait…"):
    """Show a simple full-window overlay with a message during startup.

    Can be safely called immediately after `init()` and multiple times to
    update the text. Use `hide_startup_overlay()` to remove it.
    """
    global startup_overlay, startup_overlay_label
    if window is None or root_frame is None:
        return
    if startup_overlay is None:
        startup_overlay = tk.Frame(root_frame, bg=color_background)
        # cover the entire window client area
        startup_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        startup_overlay_label = tk.Label(
            startup_overlay,
            text=message,
            fg=color_white,
            bg=color_background,
            font=("Helvetica", 16, "bold")
            )
        startup_overlay_label.place(relx=0.5, rely=0.5, anchor="center")
    else:
        try:
            startup_overlay_label.config(text=message)
            startup_overlay.lift()
        except Exception:
            pass


def hide_startup_overlay():
    """Hide and destroy the startup overlay if it exists."""
    global startup_overlay, startup_overlay_label
    if startup_overlay is not None:
        try:
            startup_overlay.destroy()
        except Exception:
            pass
    startup_overlay = None
    startup_overlay_label = None


# set_webcam_image and set_pose_image are supposed to be called in the
# update-loop in main.py
def set_webcam_image(webcam, webcam_skeleton, only_skeleton):
    """Update the webcam preview image according to the selected preview mode.

    The input images are numpy arrays; this function mirrors the image for the
    user, letterboxes it to the fixed preview size, and updates the label.
    """
    global array
    match selected_preview.get():
        case "Webcam":
            array = webcam
        case "Webcam + Skeleton":
            array = webcam_skeleton
        case "Skeleton Only":
            array = only_skeleton
        case _:
            array = webcam

    if array is None:
        return

    array = array[:, ::-1, :]  # flip the camera horizontally only for the user
    # image = ImageTk.PhotoImage(Image.fromarray(array).resize((
    # webcam_image_width, webcam_image_height), Image.LANCZOS))

    # calculate the source and destination image ratios
    img = Image.fromarray(array)
    src_w, src_h = img.size
    dst_w_base, dst_h_base = webcam_image_width, webcam_image_height
    if selected_mode is not None and selected_mode.get() == "Collect":
        scale = collect_scale
    else:
        scale = 1.0

    dst_w = int(dst_w_base * scale)
    dst_h = int(dst_h_base * scale)

    src_ratio = src_w / src_h
    dst_ratio = dst_w / dst_h

    # keep the aspect ratio and resize the image
    if src_ratio > dst_ratio:
        new_w = dst_w
        new_h = int(dst_w / src_ratio)
    else:
        new_h = dst_h
        new_w = int(dst_h * src_ratio)

    # add black bars to the resized image to maintain webcam preview size
    img = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (dst_w, dst_h), (0, 0, 0))
    canvas.paste(img, ((dst_w - new_w) // 2, (dst_h - new_h) // 2))
    image = ImageTk.PhotoImage(canvas)

    label_webcam.config(image=image)
    label_webcam.image = image


def set_gamepad_image(updated_gamepad_image):
    """Update the virtual gamepad preview image using the logic of
    gamepad_visualizer.py."""
    if updated_gamepad_image is None:
        return
    image = ImageTk.PhotoImage(
        updated_gamepad_image.resize(
            (gamepad_image_width, gamepad_image_height), Image.LANCZOS
            )
        )
    label_virtual_gamepad_visualizer.config(image=image)
    label_virtual_gamepad_visualizer.image = image


def update_pose(new_pose):
    global pose
    pose = new_pose


def update_pose_image():
    """Update the pose image icon based on the current pose name."""
    valid_poses = [
        "standing", "jumping", "crouching", "throwing",
        "walking_right", "walking_left", "running_right", "running_left",
        "swimming"
        ]
    if pose in valid_poses:
        try:
            window.image_pose = ImageTk.PhotoImage(
                Image.open(
                    ph.resource_path(os.path.join("images", pose + ".png"))
                    ).resize(
                    (100, 100), Image.LANCZOS
                    )
                )
        except FileNotFoundError:
            print("Error: File not found")
            sys.exit(1)
    else:
        # Display question mark symbol if unknown pose is performed
        window.image_pose = ImageTk.PhotoImage(
            Image.open(path_image_pose_default).resize(
                (100, 100),
                Image.LANCZOS
                )
            )

    label_pose_visualizer.config(image=window.image_pose)
    label_pose_visualizer.image = window.image_pose


def update_pose_text():
    label_current_pose.config(text="Current Pose:" + pose)


def update_debug_landmarks(landmarks):
    label_debug_landmarks.config(
        text=landmarks if allow_debug_info.get() else ""
        )


def apply_mode(mode: str):
    """Switch the UI between play modes and collect mode.

    Args:
        mode: One of "Simple", "Full-body", "Collect".
    """
    global label_collect_status, button_collect_start
    global label_virtual_gamepad_visualizer, label_pose_visualizer, \
        label_current_pose
    global checkbox_toggle_inputs, allow_debug_info, send_keystrokes
    global geometry_normal, geometry_collect, previous_mode_collect

    if not previous_mode_collect:
        get_geometry()

    if mode == "Collect":
        previous_mode_collect = True
        allow_debug_info.set(1)
        send_keystrokes.set(0)
        window.resizable(True, True)
        if platform.system() != "Darwin":
            if geometry_collect is not None:
                window.geometry(geometry_collect)
        elif platform.system() == "Darwin":
            window.state("zoomed")
        window.resizable(False, False)

        label_collect_status.configure(font=font_collect_large)

        # Hide widgets that are not relevant
        checkbox_toggle_inputs.grid_remove()
        label_virtual_gamepad_visualizer.grid_remove()
        label_pose_visualizer.grid_remove()
        label_current_pose.grid_remove()

        # Display collect mode specific widgets
        label_collect_status.grid()
        button_collect_start.grid()
        _set_collect_button(starting=False)

    else:
        previous_mode_collect = False
        window.resizable(True, True)
        window.geometry(geometry_normal)

        window.resizable(False, False)
        label_collect_status.configure(font=font_collect_normal)

        checkbox_toggle_inputs.grid()

        # Display play mode specific widgets
        label_virtual_gamepad_visualizer.grid()
        label_pose_visualizer.grid()
        label_current_pose.grid()

        # Hide collect mode specific widgets
        label_collect_status.grid_remove()
        _set_collect_button(starting=False)
        button_collect_start.grid_remove()


def _set_collect_button(starting: bool):
    """Configure the collect button text and callback based on state.

    Args:
        starting: If True, the button becomes a “Stop collecting” button.
    """
    if starting:
        button_collect_start.config(
            text="Stop Collecting",
            command=stop_collect_sequence
            )
    else:
        button_collect_start.config(
            text="Start Collecting",
            command=start_collect_sequence
            )


# Collecting mode-specific functions:
def _schedule_after(ms, func, *args):
    aid = window.after(ms, func, *args)
    after_handles.append(aid)
    return aid


def _cancel_scheduled():
    while after_handles:
        aid = after_handles.pop()
        try:
            window.after_cancel(aid)
        except tk.TclError:
            pass


def start_collect_sequence():
    """Start a full pose collection run with randomized pose order."""
    global collecting, collect_stop, current_run_csv, collection_order
    if collecting:
        return
    collect_stop = False
    collecting = True
    _cancel_scheduled()
    # Randomize the order of collection steps for this run
    collection_order = random.sample(COLLECTION_STEPS, len(COLLECTION_STEPS))

    runs_dir = Path(state_manager.get_data_folder_path())

    user = getpass.getuser()
    current_run_csv = str(
        runs_dir / f"pose_samples_{user}_"
                   f"{datetime.now().strftime("%d.%m.%Y_%H.%M")}.csv"
        )
    label_collect_status.config(text="Starting Sequence…")
    _set_collect_button(starting=True)
    run_collect_step(0)


def stop_collect_sequence():
    global collecting, collect_stop
    collect_stop = True
    collecting = False
    _cancel_scheduled()
    label_collect_status.config(text="Stopped.")
    _set_collect_button(starting=False)


def run_collect_step(index: int):
    """Run a single step of the collection sequence.

    Advances through COLLECTION_STEPS (or the randomized order) and
    triggers countdown and recording for each pose.
    """
    global collecting, collect_stop, collection_order
    if collect_stop:
        _set_collect_button(starting=False)
        return

    steps = collection_order if collection_order else COLLECTION_STEPS

    if index >= len(steps):
        _cancel_scheduled()
        label_collect_status.config(text="Finished.")
        collecting = False
        collect_stop = False
        collection_order = None
        _set_collect_button(starting=False)
        return

    pose_name, seconds = steps[index]
    show_collect_countdown(3, pose_name, seconds, index)


def show_collect_countdown(n: int, pose_name: str, seconds: float, index: int):
    """Show a countdown before recording a specific pose.

    When the countdown reaches zero, starts recording for the given pose.
    """
    if collect_stop:
        return
    if n == 0:
        label_collect_status.config(
            text=f"Rec: {pose_name} ({int(seconds)}s)"
            )
        if not collect_stop:
            threading.Thread(
                target=record_collect_pose,
                args=(pose_name, seconds, index),
                daemon=True
                ).start()
            show_recording_countdown(int(seconds), pose_name, index)
        return

    label_collect_status.config(text=f"{pose_name} in {n} …")
    _schedule_after(
        1000, show_collect_countdown, n - 1, pose_name, seconds,
        index
        )


def show_recording_countdown(remaining: int, pose_name: str, index: int):
    if collect_stop:
        return
    if remaining <= 0:
        return
    label_collect_status.config(text=f"Rec: {pose_name} ({remaining}s)")
    _schedule_after(
        1000, show_recording_countdown, remaining - 1, pose_name,
        index
        )


def record_collect_pose(pose_name: str, seconds: float, index: int):
    """Record pose samples for the given duration and schedule the next step.

    This function runs in a worker thread and calls collect.main()
    with appropriate CLI arguments.
    """
    if collect_stop:
        return
    global current_run_csv
    # Lazy-import to avoid heavy MediaPipe dependency during app startup.
    from super_mario_motion import collect as _collect
    sys.argv = [
        "collect.py",
        "--label", pose_name,
        "--seconds", str(seconds),
        "--csv", current_run_csv,
        "--fps", str(Settings.webcam_fps),
        "--source", "auto",
        ]
    _collect.main()
    if not collect_stop:
        _schedule_after(500, lambda: run_collect_step(index + 1))


# Takes in a Path and opens this path as a file in the default browser
def open_browser(path):
    webbrowser.open_new_tab(path.as_uri())


# gets called by the "Help"-Button, calls open_browser in a separate thread,
# so that the main thread does not have to wait for the browser to start up
# (~5 seconds)
def open_help_menu():
    if state_manager.get_standalone():
        help_path = ph.resource_path(os.path.join("help", "help_page.pdf"))
    else:
        help_path = os.path.join("docs", "help", "help_page.pdf")
    help_file_path = Path(help_path).resolve()

    threading.Thread(
        target=open_browser, args=(help_file_path,),
        daemon=True
        ).start()


def open_config():
    """Open the config file in the system's default editor/viewer.

    Uses os.startfile on Windows, "open" on macOS, and "xdg-open" on Linux.
    The actual editor depends on the user's file associations.
    """
    config_path = Path(state_manager.get_config_path())

    def _open():
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(str(config_path))
            elif system == "Darwin":
                subprocess.Popen(["open", str(config_path)])
            else:
                subprocess.Popen(["xdg-open", str(config_path)])
        except Exception as e:
            print(f"[GUI] Could not open config: {e}")

    threading.Thread(target=_open, daemon=True).start()


def update_launch_button_state():
    if button_launch_game is None or selected_control_scheme is None:
        return

    scheme = selected_control_scheme.get() or ""
    disable = (
            (
                        scheme == "Original (RetroArch)" and not
            game_launcher.retro_paths_valid) or
            (scheme == "Custom" and not game_launcher.custom_path_valid)
    )
    button_launch_game.state(["disabled"] if disable else ["!disabled"])


def config_validation():
    global label_config_warning

    if state_manager.get_invalid_config():
        print("[GUI] Creating on screen warning for config")
        if label_config_warning is None:
            label_config_warning = tk.Label(
                frame_bottom_right,
                bg=color_dark_widget,
                fg="#FFFF00",
                width=40,
                text="Invalid JSON syntax in config file.\nLoading failed.",
                font=("Helvetica", 9, "bold")
                )
            label_config_warning.grid(row=3, column=0, columnspan=2)
        else:
            label_config_warning.grid()
    else:
        if label_config_warning is not None:
            label_config_warning.grid_remove()


def reload_config():
    """Reload config.json from disk and apply changes at runtime.
    Runs in a background thread to keep the UI responsive.
    """

    def _reload():
        from super_mario_motion import user_data, input
        user_data.init()
        game_launcher.init()
        input.load_custom_keymap()
        update_launch_button_state()
        config_validation()

    threading.Thread(target=_reload, daemon=True).start()


def center_window(w, h):
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    window.geometry(f"{w}x{h}+{x}+{y}")


def get_geometry():
    global geometry_normal
    geometry_normal = window.geometry()


# os.path.join("images","webcam_sample.jpg")
# gets called by the "Start Game"-Button
def start_game_button_action():
    threading.Thread(target=game_launcher.launch_game, daemon=True).start()


def close():
    try:
        # Lazy import; may not be loaded yet.
        from super_mario_motion import vision_ml
        vision_ml.stop()
    except (RuntimeError, AttributeError, cv2.error) as e:
        print("ML shutdown warning:", e)

    try:
        # Lazy import; may not be loaded yet.
        from super_mario_motion import vision
        vision.stop_cam()
    except (
            RuntimeError, AttributeError, cv2.error, ImportError,
            NameError
            ) as e:
        print("Camera shutdown warning:", e)

    window.destroy()


def change_cam(event):
    global index
    event.widget.selection_clear()
    selected_cam_value = selected_cam.get()
    index = main.cams_available.index(selected_cam_value)
    state_manager.set_current_cam_index(index)
    print(index)
    vision.init()
