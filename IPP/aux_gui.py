# -*- coding: utf-8 -*-
import os
import locale

import wx
# Dialog that prompts for the saving of a file
def save_file_diag(self, filename, dir, wildcard='All files (*.*)|*.*'):
    dlg = wx.FileDialog(
            self, message="Save as...",
            defaultDir=dir, 
            defaultFile=filename,
            wildcard=wildcard,
            style=wx.SAVE,
            )
    
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    else:
        return None

    dlg.Destroy()
    return path

# Dialog that prompts for the opening of a file.
def open_file_diag(self, dir, wildcard='All files (*.*)|*.*'):
    dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=dir, 
            defaultFile='',
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR,
            )
    
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    else:
        return None

    dlg.Destroy()
    return path

# Returns the path chosen in the dialog
def get_path(self):
    #wildcard = "CDD files (*.cdd)|*.cdd|"     \
    #    "All files (*.*)|*.*"
    dlg = wx.DirDialog(self, "Choose a directory to put the generated files:",
                        os.getcwd() + '../',
                        style=wx.DD_DEFAULT_STYLE
                        )


    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
    else:
        return None

    dlg.Destroy()
    return path

# Pops a message with the selected tag and icon

def popup_message(self, msg, tag, icons):
    """
    Example: 
    popup_message(None, 'Message', 'Tagline', wx.ICON_EXCLAMATION)
    """
    dlg = wx.MessageDialog(self, msg, tag, icons)
    result = dlg.ShowModal()
    dlg.Destroy()
    if result == wx.ID_YES:
        return True
    else:
        return False

