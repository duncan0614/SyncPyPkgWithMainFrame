import json
import os
import re
import string
from tkinter.ttk import Style
import wx

class SettingDialog(wx.Dialog):

    stationName = ""
    stationSelected = False

    def __init__(self, *args, **kw):
        super(SettingDialog, self).__init__(*args, **kw, size = wx.Size(420, 220))
        self.SetTitle('Python Version')
        # self.SetMinSize(wx.Size(420, 300))
        # self.SetMaxSize(wx.Size(420, 600))
        self.InitUI()
        self.stationSelected = False

    def InitUI(self):

        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False) #FONTWEIGHT_BOLD
        sizer = wx.GridBagSizer(3, 3)

        panel = wx.Panel(self)
        
        font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        Version = wx.StaticText(panel, label="Python Version")
        Version.SetFont(font)
        sizer.Add(Version, pos=(0, 0), span=(1, 3), flag=wx.TOP|wx.LEFT|wx.ALIGN_CENTER, border=5)

        #STName = ["Please Select", "A9314398_M02_ASM2Test", "A9314398_M03_ASM2Test", "A9314398_M04_ASM2Test", "A9314398_M05_ASM2Test"] 
        self.cbVersion = wx.ComboBox(panel, style = wx.CB_READONLY) 
        self.cbVersion.Select(0)
        self.cbVersion.SetFont(font)
        sizer.Add(self.cbVersion, pos=(1, 0),span=(1, 3), flag=wx.TOP|wx.LEFT|wx.ALIGN_CENTER, border=5)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        btnOK = wx.Button(panel, label='OK', size=(70, 30))
        btnOK.SetFont(font)
        hbox1.Add(btnOK, flag=wx.RIGHT, border=160)
        # btnCancel = wx.Button(panel, label='Cancel', size=(70, 30))
        # btnCancel.SetFont(font)
        # hbox1.Add(btnCancel, flag=wx.BOTTOM|wx.RIGHT, border=5)
        emptyText1 = wx.StaticText(panel, label="  ")
        hbox1.Add(emptyText1, flag=wx.BOTTOM, border=25)
        sizer.Add(hbox1, pos=(4, 0), span=(1, 3), flag=wx.BOTTOM|wx.RIGHT|wx.ALIGN_RIGHT)
        
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(2)

        panel.SetSizer(sizer)

        self.Bind( wx.EVT_BUTTON, self.OnSelect, btnOK )
        # self.Bind( wx.EVT_BUTTON, self.OnCancel, btnCancel )
        self.Centre()

    def Addchoices(self, versions:list):
        for item in versions:
            self.cbVersion.Append(item)

    def OnSelect(self, event):
        
        self.stationName = self.cbVersion.GetValue() if self.cbVersion.GetValue() != "Please Select" else ""
        if self.stationName == "":
            wx.MessageBox("Please select Version.")
            return
        
        self.stationSelected = True
        self.Close()
    
    def GetSelectedVersion(self):
        return self.stationName

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    dialog = SettingDialog(None)
    msg = ["39", "310"]
    dialog.Addchoices(msg)
    dialog.ShowModal()
    if dialog.stationSelected == False:
        wx.MessageBox("close station")
    dialog.Destroy()
    print(dialog.GetSelectedVersion())
    app.MainLoop()