from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPolygon
from PyQt5.QtCore import QPoint
import psutil

HEIGHT = 60
XUSF = 160
DPOINTS = 100
WIDTH = 200
COLOR = QColor(0x000000)
BCOLOR = QColor(0x000000)

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

class Smooth:

    def average(self):
        return float(sum(self.smbuffer)) / max(len(self.smbuffer), 1)

    def __init__(self):
        self.smbuffer = []
        self.level = 5

    def smoth(self, d):
        if(len(self.smbuffer) >= self.level):
            del self.smbuffer[0]
        self.smbuffer.append(d)
        return self.average()

class Draw:
    Font = None

    POSITION = None
    AVAIBLE = None
    SCREEN = None

    def __init__(self):
        self.Font = QFont()
        self.graph = []
        self.Font.setPointSize(8)
        self.dx = 25

        
    def Ready(self): 
        net = psutil.net_io_counters( pernic = False , nowrap = True )
        self.bytes_sent_l = net.bytes_sent
        self.bytes_recv_l = net.bytes_recv
        self.sm = Smooth()

    def Move(self, x, y): return
    def Resize(self, w, h): return
    def SettingsChange(self, settings): return

    def move(self, a):
        if(len(self.graph) > DPOINTS):
            del self.graph[0]
        self.graph.append(a)

    def fillGraph(self, context, graph):
        points = []
        x = 0
        step = XUSF / DPOINTS

        points.append(QPoint(0, HEIGHT))
        for gr in graph[1:]:
            points.append(QPoint(x, HEIGHT - gr * HEIGHT))
            x+=step
        points.append(QPoint(points[len(points)-1].x(), HEIGHT))

        context.drawPolygon(QPolygon(points))


    def Draw(self, context, deltatime):
        cpupercent = self.sm.smoth(psutil.virtual_memory().percent)

        self.move(cpupercent/100)
        context.setPen(COLOR)
        context.setBrush(BCOLOR)
        self.fillGraph(context, self.graph)
        context.setFont(self.Font)
        context.drawText(XUSF+5, HEIGHT - 12, "RAM")
        context.drawText(XUSF+5, HEIGHT, toFixed(cpupercent, 1)+"%")

        


