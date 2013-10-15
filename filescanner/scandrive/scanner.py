import wx

class scanner(wx.Frame):
    
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Scanner', size=(600, 400))
        main_panel = wx.Panel(self)
        button = wx.Button(main_panel, label='exit', pos=(130, 10), size=(60, 60))
        self.Bind(wx.EVT_BUTTON, self.closebutton, button)
        self.Bind(wx.EVT_CLOSE, self.closewindow)
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = scanner(parent=None, id=-1)
    frame.Show()
    app.MainLoop()