from pathlib import Path
from windcomponents import *
from settings import *
import os
import shutil
import json
import explorer
import widget
import DefaultWidget
import re

def getSTR(strd):
    if(strd == None):
        return ""
    else:
        return str(strd)

class WidgetEmeeter:
    name: str
    desc: str
    version: str
    update: float
    uid: str
    path: str

    def getSettings(self):
        try:
            if(os.path.exists(self.dir + "/properties.json")):
                with open(self.dir + "/properties.json", "r") as f:
                    decode_s = json.JSONDecoder().decode(f.read())
                    return decode_s.get(self.uid) if decode_s.get(self.uid) != None else {}
            else:
                return {}
        except:
            return {}

    def saveSettings(self, settings):
        js = None
        try:
            if(os.path.exists(self.dir + "/properties.json")):
                with open(self.dir + "/properties.json", "r") as f:
                    js = json.JSONDecoder().decode(f.read())
            else:
                js = {}
        except:
            js = {}

        with open(self.dir + "/properties.json", "w") as f:
            js[self.uid] = settings
            f.write(json.dumps(js))

    def __init__(self, name: str, desc: str, version: str, update: float, uid: str, dir: str, path: str):
        self.name = name
        self.desc = desc
        self.version = version
        self.update = update
        self.uid = uid
        self.dir = dir
        self.path = path

class Emeeter:
    dir: str
    name: str
    desc: str
    author: str
    uid: str
    widgets: list

    def __init__(self, dir: str, name: str, desc: str, author: str, uid: str):
        self.dir = dir
        self.name = name
        self.desc = desc
        self.author = author
        self.localisation = None
        self.uid = uid
        self.widgets = []

    

def listdir_fullpath(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

async def save(a, b):
    with open(str(Path(__file__).resolve().parent) + "/data/" + a, "w") as f:
        f.write(b)

def LoadLocale():
    try:
        global WINDOWLOCALe
        WINDOWLOCALe = json.loads(open(str(Path(__file__).resolve().parent)+"/data/localisation.json").read())[LOCALe]
        print("Localization set " + LOCALe)
    except:
        print("An error occurred while loading the localization...")

class WorkWindow(QMainWindow):
    items = {}

    def __init__(self, config):
        super().__init__()
        self.active_w = []
        self.config = config
        self.setMinimumSize(800, 390)
        self.setWindowFlags(Qt.Dialog)
        self.initUI()
        
    """PRIVATE"""
    def initUI(self):
        self.theme = [
            0x000000, #Default_color
            0xffffff, #back_color
            0x008cff, #Sellected_color
            0x333333, #Active_color
            0x333333, #BACTIVE
            0xffffff,  #BACTIVE
            [
                0x363636,
                0x0066ff
            ],
            0x000000, #scrollbar
            [
                0x333333, #checkbox active
                0xfcfcfc #checkbox n active
            ]
        ]

        w = QDesktopWidget().screenGeometry()

        self.statusBar().setStyleSheet("background-color: #ffffff")

        self.setWindowTitle('Wrain')

        self.setStatus("done_01")

        self.setGeometry((w.width() - w.width() * 0.6)*0.5, (w.height() - w.height() * 0.5)*0.5, w.width() * 0.6, w.height() * 0.5)

        self.items["itemlist"] = QSpeciaList(self)

        if("empty_01" in WINDOWLOCALe):
            self.items["itemlist"].empty_text = WINDOWLOCALe["empty_01"]

        self.items["add-item"] = QButtonE(self)
        self.items["add-item"].logger = self.statusBar().showMessage

        self.items["d_tools"] = layer()
        self.items["d_tools"].setVisable(False)

        if("st_button_01" in WINDOWLOCALe and "st_button_03" in WINDOWLOCALe and "st_button_05" in WINDOWLOCALe):
            self.items["header"] = QHeader(self, [WINDOWLOCALe["st_button_01"], WINDOWLOCALe["st_button_03"], WINDOWLOCALe["st_button_05"]])
            self.items["header"].handler = self.headerTracker
        
        if("st_version_01" in WINDOWLOCALe and "st_desc_01" in WINDOWLOCALe):
            self.items["body-left"] = infoBlock(self, WINDOWLOCALe["st_version_01"], WINDOWLOCALe["st_desc_01"])
        
        self.items["body-right"] = widgetManager(self)
        self.items["body-settings"] = systemSettings(self)

        self.items["body-settings"].listener = self.settingsChangeListener

        self.items["d_tools"].add(self.items["header"])
        self.items["d_tools"].add(self.items["body-left"])
        self.items["d_tools"].add(self.items["body-right"])
        self.items["d_tools"].add(self.items["body-settings"])

        self.updateProjectList()
        self.initStartup()

    def buildDescription(self, desc, localisation):
        def replacer(math):
            print(localisation.keys())
            for local in localisation.keys():
                if(local == math.group(1)):
                    return localisation[local]
            else:
                return math.group(0)

        return re.sub(r"\{\$([aA-zZ0-9_]+)\}", replacer, desc)

    def settingsChangeListener(self, index, pd, bl):
        item = self.getSellection()
        s = item.odata.widgets[item.sellected].getSettings()
        if(index == 0):
            s["on-the-top"] = bl
        item.odata.widgets[item.sellected].saveSettings(s)

    """PUBLIC"""
    def removeSellection(self):
        index = 0
        for item in self.items["itemlist"].items:
            if(item.sellected != -2):
                del self.items["itemlist"].items[index]
                shutil.rmtree(item.odata.dir)
                self.items["d_tools"].setVisable(False)
                self.items["itemlist"].update()
            index+=1

    """PRIVATE"""
    def headerTracker(self, index):
        item = self.getSellection()

        if(index == 0):
            itemid = str(item.odata.uid + "#" + str(item.sellected))

            if(item.sellected != -1):
                if(self.getWindowByUid(itemid) == None):
                    self.startup(item)
                    if("st_button_02" in WINDOWLOCALe):
                        self.items["header"].setText(0, WINDOWLOCALe["st_button_02"])
                        self.items["itemlist"].update()
                else:
                    index = 0
                    for active in self.active_w:
                        if(str(active.id) == itemid):
                            self.setStatus("st_rm_complete_01")
                            self.active_w[index].close()
                            item.active.remove(item.sellected)
                            del self.active_w[index]
                            if("st_button_01" in WINDOWLOCALe):
                                self.items["header"].setText(0, WINDOWLOCALe["st_button_01"])
                            self.items["itemlist"].update()
                            return
                        index += 1
            return
        
        if(index == 1):
            #AUTOSTART
            if(not item.odata.widgets[item.sellected].uid in self.config.get("active_emiters")):
                self.config.get("active_emiters").append(item.odata.widgets[item.sellected].uid)
                if("st_button_04" in WINDOWLOCALe):
                    self.items["header"].setText(1, WINDOWLOCALe["st_button_04"])
                aysync.run_await(save("config.json", json.dumps(self.config, sort_keys=True, indent=4)))
            else:
                self.config.get("active_emiters").remove(item.odata.widgets[item.sellected].uid)
                if("st_button_03" in WINDOWLOCALe):
                    self.items["header"].setText(1, WINDOWLOCALe["st_button_03"])
                aysync.run_await(save("config.json", json.dumps(self.config, sort_keys=True, indent=4)))
            return
        
        if(index == 2):
            explorer.openFolder(item.odata.dir)

    """PUBLIC"""
    def getSellection(self):
        for item in self.items["itemlist"].items:
            if(item.sellected != -2):
                return item
        return -2
    """PRIVATE"""
    def updateProjectList(self):
        rt_list = []
        self.setStatus("loading_01")
        decoder = json.JSONDecoder()
        
        if(os.path.exists(installer.WORKPATH)):

            for dir in listdir_fullpath(installer.WORKPATH):
                dir = installer.WORKPATH + dir

                if(os.path.exists(dir + "/project.json")):
                    with open(dir + "/project.json") as f:
                        decoded = decoder.decode(f.read())

                        section = QTSection(decoded.get("package").get("name"))

                        section.odata = Emeeter(
                            dir,
                            decoded.get("package").get("name").replace("\n", "|"),
                            decoded.get("package").get("desc"),
                            decoded.get("package").get("author"),
                            decoded.get("uid")
                        )
                        if(os.path.exists(dir + "/localisation.json")):
                            try:
                                with open(dir + "/localisation.json") as F:
                                    local = decoder.decode(F.read())
                                    section.odata.localisation = local.get(LOCALe)
                            except:
                                self.setStatus("st_no_localisation")
                        else:
                            self.setStatus("st_no_localisation")

                        section.addHandler(self.loadWidgetMenu)

                        for wg in decoded.get("widgets"):
                            with open(dir + "/" + str(wg) + ".json") as w:
                                wdecode = decoder.decode(w.read())
                                section.addChildren(wdecode.get("widget").get("name"))
                                section.odata.widgets.append(WidgetEmeeter(
                                    wdecode.get("widget").get("name").replace("\n", "|"),
                                    wdecode.get("widget").get("description"),
                                    str(wdecode.get("widget").get("version") if wdecode.get("widget").get("version") != None else decoded.get("package").get("version")),
                                    wdecode.get("widget").get("update"),
                                    wdecode.get("uid"),
                                    dir,
                                    dir + "/" + str(wg) + ".json"
                                ))
                        
                        rt_list.append(section)
                else:
                    shutil.rmtree(dir)
            self.items["itemlist"].items = rt_list
            self.items["itemlist"].update()
            self.setStatus("done_01")
    
    """PRIVATE"""
    def loadWidgetMenu(self, data, type):
        self.items["d_tools"].setVisable(type != None and data.sellected != -1)
        sets = data.odata.widgets[data.sellected].getSettings()
        itemid = str(data.odata.uid + "#" + str(data.sellected))
        sellected = data.odata.widgets[data.sellected]
        self.items["header"].setText(-1, sellected.name)

        if(type != None):
            self.items["body-settings"].clear()

            description = sellected.desc if sellected.desc != None else WINDOWLOCALe["st_no_description"]
            description = self.buildDescription(description, data.odata.localisation if data.odata.localisation != None else {})

            if(sets != None):
                self.items["body-settings"].addParameter(WINDOWLOCALe["dr_dx11_mp"], sets.get("on-the-top") if sets.get("on-the-top") != None else False)

            if(not sellected.uid in self.config.get("active_emiters")):
                if("st_button_03" in WINDOWLOCALe):
                    self.items["header"].setText(1, WINDOWLOCALe["st_button_03"])
            else:
                if("st_button_04" in WINDOWLOCALe):
                    self.items["header"].setText(1, WINDOWLOCALe["st_button_04"])
                    
            if(self.getWindowByUid(itemid) == None):
                if("st_button_01" in WINDOWLOCALe):
                    self.items["header"].setText(0, WINDOWLOCALe["st_button_01"])
            else:
                if("st_button_02" in WINDOWLOCALe):
                    self.items["header"].setText(0, WINDOWLOCALe["st_button_02"])

            self.items["body-left"].restore()
            self.items["body-left"].setText(getSTR(sellected.version), description)
            
            self.update()
            
        return
    """PRIVATE"""

    def getWindowByUid(self, uid):
        for act in self.active_w:
            if(act.id == uid):
                return act
        else:
            return None

    """PRIVATE"""
    def startup(self, item, index = None):
        index = index if index != None else item.sellected

        DECODER = json.JSONDecoder()

        with open(item.odata.widgets[index].path) as f:
            decode_s = DECODER.decode(f.read())

            if(decode_s.get("widget") != None):
                drawer = os.path.join(item.odata.dir, str(index)+".py")
                drawername = ".py"

                if(decode_s.get("widget").get("drawer") != None):
                    drawer = os.path.join(item.odata.dir, decode_s.get("widget").get("drawer"))
                    drawername = decode_s.get("widget").get("drawer")

                    settings = Settings(None, None, item.odata.name, None)
                    if(decode_s.get("widget").get("default") != None):
                        settings = Settings(
                            decode_s.get("widget").get("default").get("width"),
                            decode_s.get("widget").get("default").get("height"),
                            item.odata.name,
                            decode_s.get("widget").get("default").get("origin")
                        )

                item.active.append(index)
                item.wid = item.odata.uid

                self.items["d_tools"].update()

                try:
                    w = widget.Widget(decode_s.get("widget"), drawer, drawername, settings, self, item.odata.uid + "#" + str(index))
                    
                    s = item.odata.widgets[index].getSettings()
                    if(s.get("x") != None and s.get("y") != None):
                        w.move(s["x"], s["y"])
                    
                    self.active_w.append(w)
                except:
                    self.setStatus("st_initialisation_error")
            else:
                self.setStatus("st_initialisation_error")

    def initStartup(self):
        emiters = []
        for item in self.items["itemlist"].items:
            index = 0
            for sl in item.odata.widgets:
                if(sl.uid in self.config["active_emiters"]):
                    print("Run "+sl.uid)
                    self.startup(item, index)
                emiters.append(sl.uid)
                index += 1
        for emiter in self.config["active_emiters"]:
            if(not emiter in emiters):
                self.config["active_emiters"].remove(emiter)
        aysync.run_await(save("config.json", json.dumps(self.config, indent=4)))

    def closeEvent(self, event):
        self.hide()
        if(len(self.active_w) == 0):
            def show():
                self.show()
                del self.active_w[0]
            if("st_open_01" in WINDOWLOCALe):
                dw = DefaultWidget.Widget(WINDOWLOCALe["st_open_01"])
                dw.show()
                dw.mousePressEvent = lambda event: show()
                self.active_w.append(dw)
        event.ignore()

    def resizeEvent(self, event):
        l_bar = self.width() * 0.4 if self.width() * 0.4 < 300 else 300
        
        self.items["itemlist"].resize(l_bar, self.height() - 52)

        self.items["add-item"].resize(l_bar, 30)
        self.items["add-item"].move(0, self.height() - 52)

        self.items["header"].move(l_bar, 0)
        self.items["header"].resize(self.width() - l_bar, 30)

        self.items["body-right"].resize(self.width() - l_bar*2, self.height() - 30 - 150)
        self.items["body-right"].move(l_bar*2, 30)

        self.items["body-left"].resize(l_bar, self.height() - 30 - 150)
        self.items["body-left"].move(l_bar, 30)

        self.items["body-settings"].resize(l_bar, 150)
        self.items["body-settings"].move(l_bar, self.height() - 150)

    #common_autostart
    def setStatus(self, status):
        if(status in WINDOWLOCALe):
            self.statusBar().showMessage(WINDOWLOCALe[status])