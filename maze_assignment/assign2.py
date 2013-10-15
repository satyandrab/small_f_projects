



###################################################################
#
#   CSSE1001 - Assignment 2
#
#   Student Number:
#
#   Student Name:
#
###################################################################


#
# Do not change the following import
#

import MazeGenerator

####################################################################
#
# Insert your code below
#
####################################################################


        

from Tkinter import * 
import tkMessageBox
import tkFileDialog

class CanvasApp(object):
    def __init__(self, master):
        self._canvas = Canvas(master, bg="black", width=500, height=00)
        self.canvas.pack(side=CENTER)

    


class MenuBar(object):

    def __init__(self, master=None):

        """Constructor: TextEditor(Tk)"""
        self._master = master
        master.title("Text Editor")

        self._filename = ''
        self._is_edited = False

        self._text = Text(master)
        self._text.pack(side=TOP, expand=True, fill=BOTH)
        self._text.bind("<Key>", self._set_edited)

        # Create the menu
        menubar = Menu(master)
        master.config(menu=menubar)

        filemenu = Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.new)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Save As...", command=self.save_as)
        filemenu.add_command(label="Exit", command=self.close)

        helpmenu = Menu(menubar)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.about)

        master.protocol("WM_DELETE_WINDOW", self.close)


        
        Frame.__init__(self, master)
        self.create_menu()
        
        self.master = Menu(self)
        
    def create_menu(self):
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File")
        menu.add_command(label="Open New Maze")
        menu.add_command(label="Save Maze")
        menu.add_command(label="Exit")

        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
            self.master.tk.call(master, "config", "-menu", self.menubar)

        self.canvas = Canvas(self, bg="white", width=400, height=400,
                             bd=0, highlightthickness=0)
        self.canvas.pack()

       

class Application(Frame):

 
    def __init__(self,master):
        self.master = master
        self.create_widgets()
        self.create_menu()

        

    def create_menu(self):
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File")
        menu.add_command(label="Open New Maze")
        menu.add_command(label="Save Maze")
        menu.add_command(label="Exit")

        



    def create_widgets(self):
        

        #"""Create three buttons"""
        controls = Frame(root)
        
        #Create first buttom
        spn1 = Spinbox(controls, from_=0, to=10,width = 2)
        spn1.pack(side=LEFT, anchor=S, pady = 10)

        
        btn1 = Button(controls, text = "New", width=5)
        btn1.pack(side=LEFT, anchor=S, pady = 10)

        controls.pack(side=LEFT, anchor=S, padx=10)

        #Create second button
        btn2 = Button(self.master, text = "Quit", command=self.master.destroy,
                      width = 5)
        btn2.pack(side=RIGHT, anchor=S, padx=10, pady=10)

        #Create third button
        btn3 = Button(self.master, text = "Reset", width = 5)
        btn3.pack(side=BOTTOM, anchor=S, pady=10)
        

root = Tk()
root.title("Maze Solver")
root.minsize(300,300)

app = Application(root)
root.mainloop()        
  
####################################################################
#
# WARNING: Leave the following code at the end of your code
#
# DO NOT CHANGE ANYTHING BELOW
#
####################################################################

def main():
    root = Tk()
    app = MazeApp(root)
    root.mainloop()

if  __name__ == '__main__':
    main()
