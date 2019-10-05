from PyQt5.QtWidgets import QFrame, QWidget, QDesktopWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics
from PyQt5.QtCore import Qt

class Widget(QWidget):

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.mask = "⚃"
        self.masked = True
        self.font = QFont()
        self.font.setPointSize(10)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.updateMove()
        
    def updateMove(self):
        a = QDesktopWidget().screenGeometry()
        if(self.masked == False):
            self.resize(QFontMetrics(self.font).width(self.text), 30)
        else:
            self.resize(QFontMetrics(self.font).width(self.mask) if QFontMetrics(self.font).width(self.mask) > 30 else 30, 30)
        self.move(a.width() - self.width(), a.height() - self.height())

    def leaveEvent(self, event):
        self.masked = True
        self.updateMove()
        self.update()

    def enterEvent(self, event):
        self.masked = False
        self.updateMove()
        self.update()

    def paintEvent(self, event):
        qt = QPainter(self)

        qt.setPen(QColor(0xffffff))

        if(self.masked == False):
            qt.drawText(self.width() * 0.5 - QFontMetrics(self.font).width(self.text) * 0.45, self.height() * 0.5 + self.font.pointSize() * 0.5, self.text)
        else:
            qt.drawText(self.width() * 0.5 - QFontMetrics(self.font).width(self.mask) * 0.45, self.height() * 0.5 + self.font.pointSize() * 0.5, self.mask)
        