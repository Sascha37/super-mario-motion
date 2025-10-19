import gui
import vision

# Function gets called every millisecond after the mainloop of the tkinter ui
def update():
    image = vision.get_latest_raw_frame()
    image_with_skeleton = vision.get_latest_skeleton()
    skeleton_active_checkbox = gui.get_boolean_skeleton_active()

    if(image is not None and image_with_skeleton is not None):
        gui.set_webcam_image(image_with_skeleton if skeleton_active_checkbox else image)    

    gui.window.after(1,update)
    
if __name__ == '__main__':
    print("Super Mario Motion started")
    vision.init()
    gui.init()

    gui.window.after(0, update)
    gui.window.mainloop()
    vision.exit = True