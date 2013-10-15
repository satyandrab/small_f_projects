from Tkinter import *
import tkFileDialog
import tkMessageBox


BUTTON_WIDTH = 10

def donothing():
    filewin = Toplevel(roof)
    button = Button(filewin, text="Do Nothing button")
    button.pack()
    

root = Tk()
root.title("Maze Solver")
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Save", command=donothing)
filemenu.add_command(label="Exit", command=root.quit)



controls = Frame(root)

reset = Button(controls, text="Reset", width=BUTTON_WIDTH)
reset.pack(side=RIGHT, anchor=S)

Quit = Button(controls, text="Quit", width=BUTTON_WIDTH)
Quit.pack(side=RIGHT, anchor=SE)

controls.pack(side=BOTTOM)


def save(self):
    """Perform the "Save" functionality."""
    if not self._filename:
        self._filename = tkFileDialog.asksaveasfilename()
    self._perform_save()

root.config(menu=menubar)
root.mainloop()
