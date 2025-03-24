import json
import os, time, subprocess, re, threading
import VersionDialog
import wx
import wx.lib.mixins.listctrl
import DefaultPackage


class AutoWidthListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):

    def __init__(self, parent, *args, **kw):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT|wx.LC_AUTOARRANGE) #|wx.LC_NO_HEADER
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

class SyncPythonPackage (wx.Frame):
    
    Worker = None
    TestResult = False
    currentPath = os.getcwd()
    _UnitSN = ""

    def __init__(self, parent):

        super(SyncPythonPackage, self).__init__(parent, title="Sync Python Package With Main Frame", size=wx.Size(550, 260), style=wx.MINIMIZE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.CLIP_CHILDREN)
        self.SetMinSize(wx.Size(550, 260))
        self.SetMaxSize(wx.Size(550, 600))
        self.SetBackgroundColour(wx.WHITE)
        self.InitUI()

        self.Centre()
        self.Show()

    def InitUI(self):
        
        # panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        sizer1 = wx.GridBagSizer(2, 2)
        
        font1 = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD, False)
        self.font_normal = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)

        buttonSizer1 = wx.BoxSizer(wx.VERTICAL)
        buttonSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.GetBtn = wx.Button(self, label='Get Package', size=(140, 30))
        self.GetBtn.SetFont(font1)
        buttonSizer1.Add(self.GetBtn)

        self.SetBtn = wx.Button(self, label='Install Package', size=(140, 30))
        self.SetBtn.SetFont(font1)
        buttonSizer2.Add(self.SetBtn)

        sizer1.Add(buttonSizer1, pos=(0, 1), flag=wx.TOP  | wx.ALIGN_CENTER, border=10)
        sizer1.Add(buttonSizer2, pos=(2, 1), flag=wx.BOTTOM | wx.ALIGN_CENTER, border=10)
        for i in range(3):
            sizer1.AddGrowableRow(i)

        hbox.Add(sizer1, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        sizer2 = wx.GridBagSizer(0, 0)
        self.list = AutoWidthListCtrl(self)
        self.list.AlwaysShowScrollbars(True, True)
        self.list.SetFont(font1)
        self.list.InsertColumn(0, "Package", width=200)
        
        # col = self.list.GetColumn(0)
        # col.SetText('HOWDY')
        # self.list.SetColumn(0, col)
        self.list.InsertColumn(1, "Version", width=150)
        #self.list.SetTextColour(wx.GREEN)
        
        # self.MsgText = wx.TextCtrl(panel, size = (400,250), style=wx.TE_MULTILINE | wx.TE_READONLY)
        # self.MsgText.SetFont(font1)
        
        sizer2.Add(self.list, pos=(0, 0), flag=wx.TOP | wx.EXPAND | wx.RIGHT, border=10)
        sizer2.AddGrowableRow(0)

        hbox.Add(sizer2, proportion=2, flag=wx.ALL | wx.EXPAND, border=5)
        

        self.Bind(wx.EVT_BUTTON, self.OnGetPackage, self.GetBtn)
        self.Bind(wx.EVT_BUTTON, self.OnSetPackage, self.SetBtn)

        self.SetSizer(hbox)

    def CreateDefaultPackageFile(self):
        
        DefaultPack = DefaultPackage.PackageList()
        PackageList = DefaultPack.Packages

        file = open("DefaultPackage.txt", 'w')
        file.write(PackageList)
        file.close()


    def OnGetPackage(self, event):

        self.ButtonControl(False)
        self.list.DeleteAllItems()
        #self.MsgText.Clear()

        self.Worker = threading.Thread(target=SyncPythonPackage.GetTaskWorker, args=(self,))
        self.Worker.start() 

        return
    
    def OnSetPackage(self, event):

        self.ButtonControl(False)
        self.list.DeleteAllItems()
        col = self.list.GetColumn(1)
        col.SetText('Result')
        self.list.SetColumn(1, col)
        #self.list.SetTextColour(1, )
        #self.MsgText.Clear()

        self.Worker = threading.Thread(target=SyncPythonPackage.SetTaskWorker, args=(self,))
        self.Worker.start()
        
        return
    
    def GetTaskWorker(self):
        
        pathList = self.findPythonPath()
        pythonVersion = ""
        pythonPath = ''
        
        # At least have a python
        if len(pathList) == 0:
            wx.MessageBox("Cannot find any python in your computer.")
            self.ButtonControl(True)
            return
        
        # process with pathlist
        Versionmsg = []
        Pathmsg = []
        self.FindPythonVersionFromPath(pathList, Versionmsg, Pathmsg)

        
        # if have multimsg show a dialog to choose
        if len(Versionmsg) > 1:
            dialog = VersionDialog.SettingDialog(None)
            dialog.Addchoices(Versionmsg)
            dialog.ShowModal()
            dialog.Destroy()
            pythonVersion = dialog.GetSelectedVersion()
            if pythonVersion == '':
                self.ButtonControl(True)
                return
            pythonPath = Pathmsg[Versionmsg.index(pythonVersion)]

        elif len(Versionmsg) == 0:
            wx.MessageBox("Cannot find any python in your computer.")
            self.ButtonControl(True)
            return
        else:
            pythonVersion = Versionmsg[0]
            pythonPath = Pathmsg[0]

        # Data to be written
        dictionary = {
            "PythonVersion": pythonVersion
        }
        
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
        
        # Writing to config.json
        with open("PythonPackageList.json", "w") as outfile:
            outfile.write(json_object)

        ret = self.WritePythonPackageIntoText(pythonPath)

        if len(ret) == 0:
            wx.MessageBox("Cannot find any python package in your PC.")
            self.ButtonControl(True)
            return
        
        row = 0
        
        for item in ret:
            self.list.InsertItem(row, item)
            self.list.SetItem(row, 1, ret[item])
            self.list.SetItemFont(row, self.font_normal)
            row += 1
            #self.MsgText.AppendText(str)

        wx.MessageBox(f"Python package get finish! Your Python version is {pythonVersion}")
        self.ButtonControl(True)
        return
    
    def SetTaskWorker(self):
        pathList = self.findPythonPath()
        pythonVersion = ""
        pythonPath = ''

        # At least have a python
        if len(pathList) == 0:
            wx.MessageBox("Cannot find any python in your computer.")
            self.ButtonControl(True)
            return
        
        # process with pathlist
        Versionmsg = []
        Pathmsg = []
        self.FindPythonVersionFromPath(pathList, Versionmsg, Pathmsg)

        # if have multimsg show a dialog to choose
        if len(Versionmsg) > 1:
            dialog = VersionDialog.SettingDialog(None)
            dialog.Addchoices(Versionmsg)
            dialog.ShowModal()
            dialog.Destroy()
            pythonVersion = dialog.GetSelectedVersion()
            if pythonVersion == '':
                self.ButtonControl(True)
                return
            pythonPath = Pathmsg[Versionmsg.index(pythonVersion)]

        elif len(Versionmsg) == 0:
            wx.MessageBox("Cannot find any python in your computer.")
            self.ButtonControl(True)
            return
        else:
            pythonVersion = Versionmsg[0]
            pythonPath = Pathmsg[0]

        msg = self.readfile()
        if len(msg) == 0:
            self.ButtonControl(True)
            return

        if "PythonVersion" not in msg:
            wx.MessageBox("config.json header is wrong!")
            self.ButtonControl(True)
            return

        ConfigPythonVersion = msg["PythonVersion"]

        sameVersion = False

        if pythonVersion != ConfigPythonVersion:
            ret = wx.MessageBox((f"Your python version is {ConfigPythonVersion}, but the package list is from {pythonVersion},\n"
                "Press OK to continue if you still want continue."), "Message Box", wx.YES_NO| wx.NO_DEFAULT | wx.ICON_QUESTION)
            if ret == 8:
                self.ButtonControl(True)
                return
            sameVersion = False
        else:
            sameVersion = True
        
        del msg["PythonVersion"]
        row = 0

        for item in msg:
            result = []

            try:
                if sameVersion:
                    ret = self.ProcessCmd(f"{pythonPath} -m pip install {item}=={msg[item]}", result, 60)
                    #ret = os.system(f"{pythonPath} -m pip install {packageList[0]}=={packageList[1]}")
                    if not ret:
                        ret = self.ProcessCmd(f"{pythonPath} -m pip install {item}", result, 60)
                        #ret = os.system(f"{pythonPath} -m pip install {packageList[0]}")
                else:
                    ret = self.ProcessCmd(f"{pythonPath} -m pip install {item}", result, 60)
                    #ret = os.system(f"{pythonPath} -m pip install {packageList[0]}")
                self.list.InsertItem(row, item)
                if ret:
                    self.list.SetItem(row, 1, "SUCCESS")
                else:
                    self.list.SetItem(row, 1, "FAIL")
                self.list.SetItemFont(row, self.font_normal)
                self.list.ScrollLines(row)
                row += 1
                #self.MsgText.AppendText(f"{packageList[0]} install finish.\n")
            except Exception as ex:
                wx.MessageBox(f"Exception: {ex}")
                self.ButtonControl(True)
                return
        
        # ret = re.findall(r"(\S+)[Pp]ython.exe", pythonPath)
        # if len(ret) != 0:
        #     folders = os.listdir(f"{ret[0]}Lib\site-packages")
        #     for item in folders:
        #         if "~x" in item:
        #             os.rmdir(f"{ret[0]}Lib\site-packages\{item}")
            
        wx.MessageBox(f"Python package install finish!")
        self.ButtonControl(True)
        return
    
    def ButtonControl(self, OnOff:bool):
        self.GetBtn.Enable(OnOff)
        self.SetBtn.Enable(OnOff)

    def readfile(self) -> list:
        try:
            msg = {}

            if os.path.exists("PythonPackageList.json"):
                with open("PythonPackageList.json", 'r') as obj:
                    msg = json.load(obj)               
            else:

                if not os.path.exists("DefaultPackage.json"):
                    # self.CreateDefaultPackageFile()
                    wx.MessageBox("Cannot find PythonPackageList.json or DefaultPackage.json")
                    return {}
                with open("DefaultPackage.json", 'r') as obj:
                    msg = json.load(obj)
            return msg
        
        except IOError:
            wx.MessageBox(IOError)
            return {}
    
    def findPythonPath(self): 
        
        msg = []
        cmd = "py --list-paths"
        ret = self.ProcessCmd(cmd, msg)
        if not ret:
            return []
        return msg
    
    def WritePythonPackageIntoText(self, path:str):
        
        result = []      
        # cmd = f'{path} -m pip list > "{self.currentPath}\\PythonPackageList.txt"'
        cmd = f'{path} -m pip list'
        if not self.ProcessCmd(cmd, result):
            return {}
        
        # ret = os.system(cmd)
        # msg = self.readfile()
        #time.sleep(0.5)

        with open("PythonPackageList.json", 'r') as obj:
            msg = json.load(obj)

        for item in result:
            ret = self.findPackageAndVersion(item)
            if len(ret) == 1:
                msg[ret[0][0]] = ret[0][1]

           
        
        # Serializing json
        json_object = json.dumps(msg, indent=4)

        # Writing to sample.json
        with open("PythonPackageList.json", "w") as outfile:
            outfile.write(json_object)

        del msg["PythonVersion"]    
        
        return msg
    
    def findPackageAndVersion(self, item:str):
        return re.findall(r"([\w-]+)\s+([\d.]+)", item)

    def FindPythonVersionFromPath(self, pathList:list, Versionmsg:list, Pathmsg:list) -> str:
        for path in pathList:
            ret = re.findall(r"Python[\d]+", path)
            if len(ret) == 1:
                ret = re.split(r"\s+", path)
                if len(ret) >= 2:
                    version = re.findall(r"[\d]+.[\d]+", ret[0])
                    Versionmsg.append(version[0])
                    Pathmsg.append(ret[1])
                    break

    def ProcessCmd(self, cmd:str, msg:list, timeout:float = 5.0, err="ignore"):
        # ex: cmd = "tool.exe arg1 arg2 art3"
        # return response into msg list
        #
        try:

            StartTime = time.time()
            #args = cmd.split(" ")
            #Launches 'command' windowless and waits until finished
            # startupinfo = subprocess.STARTUPINFO()
            # proc = Popen(args, startupinfo=startupinfo)
            # proc = Popen(args, creationflags = subprocess.CREATE_NO_WINDOW)
            # proc.wait() == 0

            # error: add 'ignore' to avoid illegal multibyte sequence error
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, errors=err, creationflags = subprocess.CREATE_NO_WINDOW)

            while True:
                output = proc.stdout.readline()
                output = output.strip()
                
                return_code = proc.poll()
                if return_code is not None:
                    #msg.append(str(return_code))
                    if return_code != 0:
                        return False
                    break
                if time.time() - StartTime > timeout:
                    msg.append("timeout")
                    break

                if len(output) == 0:
                    continue
                # print(output)
                msg.append(output)

        except Exception as ex:
            print(ex)
            return False
        return True

if __name__ == '__main__':

    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    

    frm = SyncPythonPackage(None)
    ret = frm.findPythonPath()

    for item in ret:
        ret = re.findall(r"Python[\d]+", item)
        if len(ret) == 1:
            list = re.split(r"\s+", item)
            
            break
    
    print(list)


    app.MainLoop()