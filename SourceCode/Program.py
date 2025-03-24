"""
Copyright (c) 2022 SINBON Electronics Co., Ltd.
Design & Development by EMS DDE330

Main program
Python Version:3.9.13
IDE:Visual Studio Code 1.68.0
"""

import wx
from MainFrame import SyncPythonPackage

class Program():

    _instance = None

    @staticmethod
    def Instance():
        if Program._instance is None:
            Program()
        return Program._instance

    def __init__(self):
        if Program._instance is None:
            self._id = id(self)
            Program._instance = self      

    def IsAppRunning(self):
        self.name = "SyncPythonPackage"
        self.instance = wx.SingleInstanceChecker(self.name, path='lockfiles') # actually path isn't used in Win32
        if self.instance.IsAnotherRunning():
            wx.MessageBox("The " + self.name + " application is already running.", "Warning", wx.OK | wx.ICON_WARNING)
            return True

        self.EDIUploadView = SyncPythonPackage(None)

        return False 

if __name__ == '__main__':
    app = wx.App()
    if not Program.Instance().IsAppRunning():
        app.MainLoop()
