import gui
import vision

# Function gets called every millisecond after the mainloop of the tkinter ui
def update():
    gui.window.after(1,update)

if __name__ == '__main__':
    print("Super Mario Motion started")
    vision.init()
    gui.init()

    gui.window.after(0, update)
    gui.window.mainloop()
    
