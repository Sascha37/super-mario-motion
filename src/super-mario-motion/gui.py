import tkinter as tk
from PIL import ImageTk, Image
from pathlib import Path

height = 650
width = 700
background_color = '#141618'

default_image_path = Path(__file__).parent / "data" / 'webcam_sample.jpg'

default_image_top_padding = 50

def init():
    global window     
    window = tk.Tk()

    window.title('Super Mario Motion')
    window.minsize(height,width)
    window.maxsize(height,width)

    window.configure(background=background_color)

    default_image = ImageTk.PhotoImage(Image.open(default_image_path))
    image_panel = tk.Label(window, image = default_image)
    image_panel.pack(pady = default_image_top_padding)

    print(Path(__file__).name + " initialized")

def update_image_panel(new_image):
    window.image_panel = tk.Label(window, image = default_image)