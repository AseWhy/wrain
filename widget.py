
import threading
import time
import json
import os.path as path
import imp
import sys
import inspect
import color_parser
from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtGui import QPainter, QColor
from inspect import signature

def is_nubmer(obj):
    return type(obj) == int or type(obj) == float

def current_milli_time():
    return int(round(time.time() * 1000))

class Widget(QWidget):
    def __init__(self, decode_s, drawer, drawername, settings, mainwindow, id, parent = None):
        super().__init__(parent)
        self.reset(decode_s, drawer, drawername, settings)
        self.mainwindow = mainwindow
        self.id = id
        
        if(self.Drawer.Ready != None):
            self.Drawer.Ready()

        self.initWidget()
        print(self.printMessage() + "Initialisation done uid " + str(self.id))

    """PRIVATE"""
    def mousePressEvent(self, event):
        self.mainwindow.show()
        event.ignore()

    """PRIVATE"""
    def dPrint(self, *args): 
        for arg in args:
            print(self.printMessage() + arg)

    """PRIVATE"""
    def reset(self, decode_s, drawer, drawername, settings):
        if(decode_s == None):
            raise Exception("["+settings.projectName+"] Incorrect widget init file")

        if(decode_s.get("name") != None):
            self.Name = decode_s.get("name")
        else:
            raise Exception("["+settings.projectName+"] Incorrect widget init file. Missing Nane field.")

        #Default
        width = settings.defaultWidth
        height = settings.defaultHeight
        opacity = 1
        Flags = Qt.WindowStaysOnBottomHint | Qt.NoDropShadowWindowHint

        self.Project = settings.projectName
        self.DrawerInit(drawer, drawername)

        if(decode_s.get("size") != None and decode_s.get("size").get("width") != None and is_nubmer(decode_s.get("size").get("width"))):
            width = decode_s.get("size").get("width")
        if(decode_s.get("size") != None and decode_s.get("size").get("height") != None and is_nubmer(decode_s.get("size").get("height"))):
            height = decode_s.get("size").get("height")

        if(decode_s.get("opacity") != None and is_nubmer(decode_s.get("opacity"))):
            opacity = decode_s.get("opacity")
            if(opacity > 1):
                opacity = 1
            else:
                 if(opacity < 0):
                    opacity = 0
            print(self.printMessage() + "Frame opacity is " + str(opacity))
        
        if(decode_s.get("update") != None and is_nubmer(decode_s.get("update"))):
            self.UpdateRate = decode_s.get("update")


        print(self.printMessage() + "Inited new window with " + str(width) + "x" + str(height))
        self.UpdateMetrixR(width, height)

        if(decode_s == None or decode_s.get("hide_title") == True):
            Flags = Flags | Qt.FramelessWindowHint
            print(self.printMessage(1) + "Title was be hide")

        if(decode_s == None or decode_s.get("hide_toolbar") == True):
            Flags = Flags | Qt.Tool
            print(self.printMessage(1) + "Toolbar was be hide")
            
        if(decode_s.get("tr-bg") != None and decode_s.get("tr-bg") == True):
            self.setAttribute(Qt.WA_TranslucentBackground)
            print(self.printMessage(1) + "Set a transparent background")

        if(decode_s.get("bg-color") != None):
            self.Background = color_parser.parser(decode_s.get("bg-color"))
            self.Background.Color = QColor(self.Background.Color)

        self.setWindowFlags(Flags)
        self.setWindowOpacity(opacity)
        self.setOrigin(settings.origin)

    """PRIVATE"""
    def setOrigin(self, index):
        q = QDesktopWidget().screenGeometry()

        if(index == 0):
            self.UpdateMetrixM(q.width() - self.width(), 0)
        elif(index == 1):
            self.UpdateMetrixM(q.width() - self.width(), (q.height()*0.5) - (self.height()*0.5))
        elif(index == 2):
            self.UpdateMetrixM(q.width() - self.width(), q.height() - self.height())
        elif(index == 3):
            self.UpdateMetrixM(q.width()*0.5 - self.width()*0.5, 0)
        elif(index == 4):
            self.UpdateMetrixM(q.width()*0.5 - self.width()*0.5, (q.height()*0.5) - (self.height()*0.5))   
        elif(index == 5):
            self.UpdateMetrixM(q.width()*0.5 - self.width()*0.5, q.height() - self.height())
        elif(index == 6):
            self.UpdateMetrixM(0, 0)
        elif(index == 7):
            self.UpdateMetrixM(0, (q.height()*0.5) - (self.height()*0.5))   
        elif(index == 8):
            self.UpdateMetrixM(0, q.height() - self.height())

    """PRIVATE"""
    def setDrawer(self):
        q = QDesktopWidget().screenGeometry()
        a = QDesktopWidget().availableGeometry()

        if(hasattr(self.Drawer, "SCREEN")):
            self.Drawer.SCREEN = {
                "width": q.width(),
                "height": q.height()
            }

        if(hasattr(self.Drawer, "AVAIBLE")):
            self.Drawer.AVAIBLE = {
                "width": a.width(),
                "height": a.height()
            }

        if(hasattr(self.Drawer, "POSITION")):
            self.Drawer.POSITION = {
                "x": 0,
                "y": 0
            }
        
        if(hasattr(self.Drawer, "Move")):
            sign = signature(self.Drawer.Move)
            if(len(sign.parameters) == 2):
                self.Drawer.Move = self.UpdateMetrixM
            else:
                print(self.printMessage() + "Invalid signature Move"+str(sign)+" takes " + str(len(sign.parameters)) + " parameters when get 2")
        
        if(hasattr(self.Drawer, "Resize")):
            sign = signature(self.Drawer.Resize)
            if(len(sign.parameters) == 2):
                self.Drawer.Resize = self.UpdateMetrixR
            else:
                print(self.printMessage() + "Invalid signature Resize"+str(sign)+" takes " + str(len(sign.parameters)) + " parameters when get 2")

    """PRIVATE"""
    #Creates a main render class
    def DrawerInit(self, drawer, drawername):
        Drawer = imp.load_source(drawername, drawer)
        Drawer.print = self.dPrint

        if(inspect.isclass(Drawer.Draw) and hasattr(Drawer.Draw, "Draw")):
            self.Drawer = Drawer.Draw()
            self.setDrawer()
        else:
            raise Exception(self.printMessage() + "Failed to init " + drawername + " missing correct class \"Draw\"")

    """PRIVATE"""
    def printMessage(self, level = 0):
        tabs = ""
        for _ in range(0, level):
            tabs += "\t"
        return "-> " + tabs + "[" +self.Project + "." + self.Name + "] "

    """PRIVATE"""
    def initWidget(self):
        self.LastUpdate = current_milli_time()
        self.timer = QBasicTimer()
        self.timer.start(self.UpdateRate, self)
        self.show()

    """PRIVATE"""
    def timerEvent(self, e):
        self.update()

    """PRIVATE"""
    def paintEvent(self, event):
        ct = current_milli_time()
        qt = QPainter(self)

        if(self.Background != None):
            qt.setOpacity(self.Background.Opacity)
            qt.fillRect(0, 0, self.width(), self.height(),  self.Background.Color)
            qt.setOpacity(1)

        self.Drawer.Draw(qt, (ct - self.LastUpdate) / self.UpdateRate)
        self.LastUpdate = ct

    """PROTECTED"""
    def UpdateMetrixM(self, x, y):
        if(hasattr(self.Drawer, "POSITION")):
            self.Drawer.POSITION = {
                "x": x,
                "y": y
            }
        self.move(x, y)
    
    """PROTECTED"""
    def UpdateMetrixR(self, x, y):
        self.resize(x, y)

        if(hasattr(self.Drawer, "SIZE")):
            self.Drawer.SIZE = {
                "width": self.width(),
                "height": self.height()
            }