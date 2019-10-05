from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QTimer
import FileDialog
import installer
import os
import aysync
import json

WINDOWLOCALe = {}
LOCALe = "RU_ru" #Default
LISTENERs = []

class layer:
    def __init__(self):

        self.visable = True
        self.elements = []

    def add(self, element):

        self.elements.append(element)
        if(not self.visable):
            element.hide()
        else:
            element.show()

    def setVisable(self, vsbl):

        self.visable = vsbl
        for el in self.elements:
            if(not self.visable):
                el.hide()
            else:
                el.show()

    def update(self):

        for el in self.elements:
            el.update()

class QTSection:
    name = None,
    children = []

    def __init__(self, name):
        self.name = name
        self.children = []
        self.sellected = -2
        self.handler = None
        self.odata = None
        self.wid = None
        self.active = []

    def addChildren(self, children):
        self.children.append(children)

    def invoke(self, type):
        if(self.handler != None):
            self.handler(self, type)

    def addHandler(self, handler):
        self.handler = handler

    def mousePressEvent(self, event):
        if(self.handler != None):
            self.handler(event)

class QButtonE(QFrame):
    
    def __init__(self, target):
        super().__init__(target)
        self.target = target
        self.theme = target.theme
        self.font = QFont()
        self.font.setPointSize(12)
        self.setMouseTracking(True)
        self.sellected = -1
        self.backgrounds = [
            0x0b4499,
            0x0b997d,
            0x99570b
        ]
        self.texts = [
            "✚",
            "♻",
            "✉"
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font)
        
        painter.fillRect(0, 0, self.width(), self.height(), QColor(self.theme[1]))

        dev = (self.width()/300)*2

        for i in range(0, 3):
            pos = 5+i*self.height()*dev+2*(i*2)
            if(i != self.sellected):
                painter.setPen(QColor(self.backgrounds[i]))
                painter.drawRect(pos, 5, self.height()*dev, self.height()-10)
                painter.drawText(pos + (self.height() * dev) * 0.5 - QFontMetrics(self.font).width(self.texts[i])*0.5, self.height()*0.5+self.font.pointSize()*0.5, self.texts[i])
            else:
                painter.fillRect(pos, 5, self.height()*dev, self.height()-10, QColor(self.theme[4]))
                painter.setPen(QColor(self.backgrounds[i]))
                painter.drawRect(pos, 5, self.height()*dev, self.height()-10)
                painter.setPen(QColor(self.theme[5]))
                painter.drawText(pos + (self.height() * dev) * 0.5 - QFontMetrics(self.font).width(self.texts[i])*0.5, self.height()*0.5+self.font.pointSize()*0.5, self.texts[i])

    def leaveEvent(self, event):
        self.sellected = -1
        self.update()

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        dev = (self.width()/300)*2
        if(y > 5 and y < self.height() - 5):
            for i in range(0, 3):
                if(x > 5+i*self.height()*dev+2*(i*2) and x < 5+i*self.height()*dev+2*(i*2) + self.height() * dev):
                    self.sellected = i
                    self.update()
                    self.setCursor(Qt.PointingHandCursor)
                    return
        self.sellected = -1
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def mousePressEvent(self, event):
        x = event.x()
        dev = (self.width()/300)*2
        for i in range(0, 3):
            if(x > 5+i*self.height()*dev+2*(i+1) and x < 5+i*self.height()*dev+2*(i+1) +self.height()*dev):
                self.sellected = i

                if(i == 0):
                    self.installWidget()
                elif(i == 1):
                    self.removeWidget()
                elif(i == 2):
                    self.configureWidget()

                self.update()
                return
        self.sellected = -1
        self.update()

    def installWidget(self):
        file = FileDialog.FileDialog().openFileNameDialog()
        if(file != None):
            aysync.run_await(installer.install(file, self.logger))
            self.target.updateProjectList()

    def removeWidget(self):
        self.target.removeSellection()
    
    def configureWidget(self):
        print("OK")

class QSpeciaList(QFrame):
    # List = [
    #   {
    #       "name": "name",
    #       "children": []
    #   }
    #   ...
    # ]
    items = []
    offset = 0
    step = 4
    whell_power = 4
    font = None
    sectionFont = None

    def __init__(self, target):
        super().__init__(target)
        self.font = QFont()
        self.theme = target.theme
        self.sectionFont = QFont()
        self.font.setPointSize(10)
        self.sectionFont.setPointSize(8)
        self.empty_text = ""
        self.setCursor(Qt.PointingHandCursor)

    def drawSections(self, painter, y, sections, item):
        painter.setFont(self.sectionFont)
        yt = self.step*2
        y = y + self.sectionFont.pointSize() + yt
        index = 0

        for sect in sections:
            if(y < 0):
                y += self.sectionFont.pointSize()+self.step*2
                yt += self.sectionFont.pointSize()+self.step*2
                if(index+2 > len(sections)):
                    y -= self.step
                    yt -= self.step
                index+=1
                continue
            
            if(index in item.active):
                painter.fillRect(0, y - self.sectionFont.pointSize()-self.step, 4, 2*self.step+self.sectionFont.pointSize(), QColor(self.theme[3]))
            if(index == item.sellected):
                painter.fillRect(0, y - self.sectionFont.pointSize()-self.step, 2, 2*self.step+self.sectionFont.pointSize(), QColor(self.theme[2]))
                
            painter.setPen(QColor(self.theme[0]))
            painter.drawText(20, y, sect)
            y += self.sectionFont.pointSize()+self.step*2
            yt += self.sectionFont.pointSize()+self.step*2
            if(index+2 > len(sections)):
                y -= self.step
                yt -= self.step

            if(y > self.height()+abs(self.offset)):
                return yt

            index+=1
        return yt

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.fillRect(0, 0, self.width(), self.height(), QColor(self.theme[1]))

        y = self.font.pointSize() + self.step + self.offset

        if(len(self.items) > 0):
            for item in self.items:
                painter.setFont(self.font)
                
                if(y > 0):
                    if(item.sellected == -1):
                        painter.fillRect(0, y - self.font.pointSize()-self.step, 5, 2*self.step+self.font.pointSize(), QColor(self.theme[2]))
                    else:
                        painter.fillRect(0, y - self.font.pointSize()-self.step, 5, 2*self.step+self.font.pointSize(), QColor(self.theme[0]))
                    
                    painter.setPen(QColor(self.theme[0]))
                    painter.drawText(10, y, item.name)

                t = self.drawSections(painter, y, item.children, item)
                y += self.font.pointSize()+self.step + t

                if(y > self.height() + self.offset):
                    return
        else:
            metrix = QFontMetrics(self.font).width(self.empty_text)
            painter.drawText(self.width() * 0.5 - metrix * 0.5, self.height() * 0.5, self.empty_text)

    def unstellect(self):
        for item in self.items:
            item.sellected = -2
    

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if(delta > 0):
            if(self.offset < 0):
                self.offset += self.whell_power*abs(delta/120)
        elif(delta < 0):
                self.offset -= self.whell_power*abs(delta/120)
        self.update()

    def mousePressEvent(self, event):
        y = event.y() - self.offset

        sstep = self.font.pointSize()+self.step
        pstep = self.sectionFont.pointSize()+self.step
        
        e_item = self.font.pointSize()+self.step

        for item in self.items:
            if(y <= e_item+self.step and y > e_item-sstep ):
                self.unstellect()
                item.sellected = -1
                item.invoke(-1)
                self.update()
                return
            else:
                childindex = 0
                e_item+=self.step*2
                for _ in item.children:
                    if(y <= e_item+pstep and y > e_item-self.step):
                        self.unstellect()
                        item.sellected = childindex
                        item.invoke(childindex)
                        self.update()
                        return
                    e_item += self.sectionFont.pointSize()+self.step*2
                    if(childindex+2 > len(item.children)):
                        e_item -= self.step
                    childindex+=1
                    
            
            e_item+=self.font.pointSize()+self.step
        
        if(len(self.items) > 0):
            self.items[0].invoke(None)
        self.unstellect()
        self.update()


class QHeader(QFrame):
    def __init__(self, target, buttons):
        super().__init__(target)
        self.font = QFont()
        self.buttonFont = QFont()
        self.buttons = buttons
        self.header = ""
        self.theme = target.theme
        self.setMouseTracking(True)
        self.handler = None
        self.active = -1
        self.font.setPointSize(14)
        self.buttonFont.setPointSize(6)

    def setHeader(self, header):
        self.header = header

    def paintEvent(self, event):
        context = QPainter(self)

        bwidth = self.width() * 0.6 - 9
        bwidth = bwidth if bwidth < 400 else 400
        bheight = self.height() * 0.7
        rwidth = self.width() * 0.4
        bmetrix = bwidth / len(self.buttons)

        context.setFont(self.font)
        context.setPen(QColor(self.theme[0]))
        context.fillRect(0, 0, self.width(), self.height(), QColor(self.theme[1]))
        context.drawText(5, self.height() * 0.5 + self.font.pointSize() * 0.5, self.header)
        context.fillRect(5 + rwidth, 0, bwidth, self.height(), QColor(self.theme[1]))

        btn_index = 0
        context.setFont(self.buttonFont)
        for btn in self.buttons:
            bpos = (self.width() - bwidth - 15) + btn_index * bmetrix + btn_index * 3
            if(btn_index != self.active):
                context.setPen(QColor(self.theme[0]))
                context.drawRect(bpos, self.height() * 0.15, bmetrix, bheight)
                context.drawText(bpos + ((bmetrix - QFontMetrics(self.buttonFont).width(btn))/2), self.height() * 0.5 + self.buttonFont.pointSize() * 0.5, btn)
            else:
                context.fillRect(bpos, self.height() * 0.15, bmetrix+1, bheight+1, QColor(self.theme[4]))
                context.setPen(QColor(self.theme[5]))
                context.drawText(bpos + ((bmetrix - QFontMetrics(self.buttonFont).width(btn))/2), self.height() * 0.5 + self.buttonFont.pointSize() * 0.5, btn)
            btn_index += 1

    def setText(self, idex, text):
        if(idex != -1):
            self.buttons[idex] = text
        else:
            self.header = text
        self.update()

    def mousePressEvent(self, event):
        if(self.handler != None):
            self.handler(self.active)

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        bwidth = self.width() * 0.6 - 9
        bwidth = bwidth if bwidth < 400 else 400
        bmetrix = bwidth / len(self.buttons)
        bheight = self.height() * 0.7

        btn_index = 0
        for btn in self.buttons:
            bpos = (self.width() - bwidth - 15) + btn_index * bmetrix + btn_index * 3
            if(x > bpos and x < bpos + bmetrix and y > self.height() * 0.15 and y < self.height() * 0.15 + bheight):
                self.active = btn_index
                self.setCursor(Qt.PointingHandCursor)
                self.update()
                return
            btn_index += 1
        self.active = -1
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def leaveEvent(self, event):
        self.active = -1
        self.setCursor(Qt.ArrowCursor)
        self.update()

class widgetManager(QFrame):
    def __init__(self, target):
        super().__init__(target)
        self.target = target
        self.theme = target.theme
        self.clicked = False
        self.setMouseTracking(True)
        self.clickpos = [
            0,0
        ]
        timer = QTimer(self)
        timer.timeout.connect(self.updateMetrix)
        timer.start(1000)
        self.updateMetrix()

    def updateMetrix(self):
        q = QDesktopWidget().screenGeometry()
        self.size = q.size()
        if(self.target.isActiveWindow()):
            self.update()
        
    def getWindowSellection(self):
        item = self.target.getSellection()
        if(item != -2 and item != -1):
            return self.target.getWindowByUid(item.odata.uid + "#" + str(item.sellected))
        else:
            return None

    def mouseMoveEvent(self, event):
        if(self.clicked):
            sellection = self.getWindowSellection()

            x = event.x() + self.clickpos[0]
            y = event.y() + self.clickpos[1]

            qr:float = self.height() / self.size.height()
            qd:float = self.width() / self.size.width()
            if(qr < qd):
                qd = qr
            rh:int = self.size.height() * qd
            rw:int = self.size.width() * qd
            ch:int = self.height() * 0.5 - rh * 0.5
            cw:int = self.width() * 0.5 - rw * 0.5
            qh:float = self.size.height() / rh
            qw:float = self.size.width() / rw
            dx:float = (rw / self.size.width())
            dy:float = (rh / self.size.height())
            qx:float = sellection.width() * dx
            qy:float = sellection.height() * dy

            x = x - cw if x - cw < rw - cw - qx else rw - cw - qx
            y = y - ch if y - ch < rh - qy else rh - qy

            sellection.move((x if x > 0 else 0) * qw,(y if y > 0 else 0) * qh)
            self.update()

    def saveSettings(self):
        sellection = self.getWindowSellection()

        if(sellection != None):
            item = self.target.getSellection()
            sett = item.odata.widgets[item.sellected].getSettings()

            sett["x"] = sellection.x()
            sett["y"] = sellection.y()

            item.odata.widgets[item.sellected].saveSettings(sett)

    def mousePressEvent(self, event):
        sellection = self.getWindowSellection()
        
        x = event.x()
        y = event.y()

        qr:float = self.height() / self.size.height()
        qd:float = self.width() / self.size.width()
        if(qr < qd):
            qd = qr
        rh:int = self.size.height() * qd
        rw:int = self.size.width() * qd
        ch:int = self.height() * 0.5 - rh * 0.5
        cw:int = self.width() * 0.5 - rw * 0.5
        dx:float = (rw / self.size.width())
        dy:float = (rh / self.size.height())
        qx:float = sellection.width() * dx
        qy:float = sellection.height() * dy

        #Detect cursor collusion
        if(x > sellection.x() * dx + cw and x < sellection.x() * dx + cw + qx and y > sellection.y() * dy + ch and y < sellection.y() * dy + qy + ch):
            #MIDDLEPOINT
            self.clickpos = [
                sellection.x() * dx + cw - x,
                sellection.y() * dy + ch - y
            ]
            self.clicked = True

    def mouseReleaseEvent(self, event):
        self.clickpos = [
            0, 0
        ]
        self.clicked = False
        self.saveSettings()

    def leaveEvent(self, event):
        self.clickpos = [
            0, 0
        ]
        self.clicked = False
        self.saveSettings()

    def paintEvent(self, event):
        context = QPainter(self)
        sellection = self.getWindowSellection()

        qr:float = self.height() / self.size.height()
        qd:float = self.width() / self.size.width()
        if(qr < qd):
            qd = qr
        rh:int = self.size.height() * qd
        rw:int = self.size.width() * qd
        ch:int = self.height() * 0.5 - rh * 0.5
        cw:int = self.width() * 0.5 - rw * 0.5
        qh:float = rh / self.size.height()
        qw:float = rw / self.size.width()

        context.fillRect(0, 0, self.width(), self.height(), QColor(self.theme[1]))

        #Test frame
        #context.drawRect(cw, ch, rw, rh)

        for wnd in self.target.active_w:
            context.fillRect(wnd.x() * qw + cw, wnd.y() * qh + ch, wnd.width() * qw, wnd.height() * qh, self.theme[6][0])

        if(sellection != None):
            context.fillRect(sellection.x() * qw + cw, sellection.y() * qh + ch, sellection.width() * qw, sellection.height() * qh, self.theme[6][1])


class infoBlock(QFrame):

    def __init__(self, target, v_text, d_text):
        super().__init__(target)
        self.theme = target.theme
        self.font = QFont()
        self.font.setPointSize(10)
        self.interval = 2
        self.field_interval = 5
        self.scrool = 0
        self.whell_power = 3
        self.eof = 0
        self.scwidth = 2
        self.fields = [
            [v_text, ""],
            [d_text, ""]
        ]

    def setText(self, v_text, d_text):
        self.fields[0][1] = v_text
        self.fields[1][1] = d_text

    def getCoif(self, text):
        metrix = QFontMetrics(self.font)
        max_w = 0

        for txt in text:
            c_w = metrix.width(txt)
            if(c_w > max_w):
                max_w = c_w

        return self.width() / max_w if max_w != 0 else 1

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if(delta > 0):
            if(self.scrool < 0):
                self.scrool += self.whell_power * abs(delta/120)
        elif(delta < 0):
            if(abs(self.scrool) < self.eof):
                self.scrool -= self.whell_power * abs(delta/120)
        self.update()

    def restore(self):
        self.eof = 0
        self.scrool = 0

    def paintEvent(self, event):
        context = QPainter(self)
        context.fillRect(0, 0, self.width(), self.height(), QColor(self.theme[1]))
        self.font.setPointSize(10)
        context.setFont(self.font)
        context.setPen(QColor(self.theme[0]))

        l_y = 5 + self.font.pointSize() + self.interval + self.field_interval
        l_s = l_y

        #Description
        render_text = (self.fields[1][0] + ": " + self.fields[1][1] if self.fields[1][0] != "" else self.fields[1][1]).split("\n")
        coif = self.getCoif(render_text)
        if(coif < 1):
            self.font.setPointSize(self.font.pointSize() * coif)
            context.setFont(self.font)

        for i in range(0, len(render_text)):
            l_y += self.font.pointSize() + self.interval
            if(l_y + self.scrool <= self.height() and l_y > 0):
                context.drawText(5, l_y + self.scrool, render_text[i])
        
        if(l_y > self.height()):
            self.eof = l_y - self.height()

        if(abs(self.scrool) > 0 and self.eof != 0):
            context.fillRect(self.width() - self.scwidth, l_s, self.scwidth, (self.height() - l_s) * (abs(self.scrool) / self.eof), QColor(self.theme[7]))

        #Version
        self.font.setPointSize(10)
        context.setFont(self.font)
        render_text = (self.fields[0][0] + ": " + self.fields[0][1] if self.fields[0][0] != "" else self.fields[0][1]).split("\n")
        context.fillRect(0, 0, self.width(), self.font.pointSize() + 5 + self.field_interval, QColor(self.theme[1]))
        context.drawText(5, self.font.pointSize() + 5, render_text[0])

class systemSettings(QFrame):

    def __init__(self, target):
        super().__init__(target)
        #[pname, bool: active]
        self.parameters = []
        self.scrool = 0
        self.theme = target.theme
        self.font = QFont()
        self.font.setPointSize(10)
        self.padding = 5
        self.d_padding = 6
        self.listener = None
    
    def clear(self):
        self.parameters = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(), QColor(self.theme[1]))
        q_line = self.padding
        for parameter in self.parameters:
            painter.fillRect(self.padding, q_line, self.font.pointSize()+self.d_padding, self.font.pointSize()+self.d_padding, QColor(self.theme[8][0]))
            if(parameter[1]):
                painter.fillRect(self.padding+self.d_padding*0.5, q_line+self.d_padding*0.5, self.font.pointSize(), self.font.pointSize(), QColor(self.theme[8][1]))
            q_line += self.font.pointSize()+self.d_padding
            painter.drawText(self.padding * 2 + self.d_padding + self.font.pointSize(), q_line - self.font.pointSize() * 0.5 + self.d_padding * 0.5, parameter[0])

    def addParameter(self, pname, active):
        self.parameters.append([pname, active])

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        q_line = self.padding
        for i in range(0, len(self.parameters)):
            dp = self.padding
            if(x > dp and x < dp+self.font.pointSize()+self.d_padding and y > q_line and y < q_line + self.font.pointSize()+self.d_padding):
                self.parameters[i][1] = not self.parameters[i][1]
                if(self.listener != None):
                    self.listener(i, self.parameters, self.parameters[i][1])
                self.update()
                return
            q_line += self.font.pointSize()+self.d_padding