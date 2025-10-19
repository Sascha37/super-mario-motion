import gui
import vision

# Function gets called every millisecond after the mainloop of the tkinter ui
def update():
    rgb = vision.get_latest_raw_frame()
    frame = vision.get_latest_skeleton()
    gui.update_image_panel(frame)

    gui.window.after(1,update)

if __name__ == '__main__':
    print("Super Mario Motion started")
    vision.init()
    gui.init()

    gui.window.after(0, update)
    gui.window.mainloop()
    
