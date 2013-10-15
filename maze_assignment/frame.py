from Tkinter import *

class Application:
  def __init__(self, parent):
    
    button_width = 6      
    
    button_padx = "2m"    
    button_pady = "1m"    

    buttons_frame_padx =  "3m"   
    buttons_frame_pady =  "2m"       
    buttons_frame_ipadx = "3m"   
    buttons_frame_ipady = "1m"   

    self.myParent = parent   
    self.buttons_frame = Frame(parent)
    
    self.buttons_frame.pack(    
      ipadx=buttons_frame_ipadx,  
      ipady=buttons_frame_ipady,  
      padx=buttons_frame_padx,    
      pady=buttons_frame_pady,    
      )    


  
    self.button1 = Button(self.buttons_frame)
    self.button1.configure(text="New")
    self.button1.focus_force()       
    self.button1.configure( 
      width=button_width,  
      padx=button_padx,     
      pady=button_pady     
      )

    self.button1.pack(side=LEFT, anchor=S)  

    
    self.button2 = Button(self.buttons_frame, command=self.buttons_frame.destroy)
    self.button2.configure(text="Quit")  
    self.button2.configure( 
      width=button_width,  
      padx=button_padx,     
      pady=button_pady     
      )
  
    self.button2.pack(side=RIGHT, anchor = S)

    self.button2 = Button(self.buttons_frame)
    self.button2.configure(text="Reset")  
    self.button2.configure( 
      width=button_width,  
      padx=button_padx,     
      pady=button_pady     
      )
  
    self.button2.pack(side=BOTTOM, anchor = S)
  
    

  
      
root = Tk()
app = Application(root)
root.mainloop()
