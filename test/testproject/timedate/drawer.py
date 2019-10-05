from PyQt5.QtGui import QColor, QFont, QFontMetrics
import datetime

def getDay(weekday):
    if(weekday == 0):
        return "Понедельник"
    elif(weekday == 1):
        return "Вторник"
    elif(weekday == 2):
        return"Среда"
    elif(weekday == 3):
        return "Четверг"
    elif(weekday == 4):
        return "Пятница"
    elif(weekday == 5):
        return "Суббота"
    elif(weekday == 6):
        return "Воскресенье"

def nexDay(day):
    if(day == 6):
        day = 0
    else:
        day += 1
    return getDay(day)

class Draw:
    Font = None

    POSITION = None
    AVAIBLE = None
    SCREEN = None

    def __init__(self):
        self.Font = QFont()
        
    def Ready(self): return
    def Move(self, x, y): return
    def Resize(self, w, h): return
    def SettingsChange(self, settings): return
    def Draw(self, context, deltatime):
        self.Font.setPointSize(28)
        context.setOpacity(1)
        now = datetime.datetime.now()
        context.setPen(QColor(0x000000))
        context.setFont(self.Font)

        hour = "0"
        minute = "0"
        second = "0"

        if(now.hour < 10):
            hour = "0"+str(now.hour)
        else:
            hour = str(now.hour)

        if(now.minute < 10):
            minute = "0"+str(now.minute)
        else:
            minute = str(now.minute)

        if(now.second < 10):
            second = "0"+str(now.second)
        else:
            second = str(now.second)

        time = hour + ":" + minute
        width = QFontMetrics(self.Font).width(time)
        context.drawText(10, 50, time)

        self.Font.setPointSize(16)
        context.setFont(self.Font)
        context.drawText(12 + width, 50, second)
        weekday = getDay(now.weekday())
        

        self.Font.setPointSize(10)
        context.setFont(self.Font)
        context.drawText(12, 65, weekday)
        context.setOpacity(0.4)
        context.drawText(15+QFontMetrics(self.Font).width(weekday), 65, nexDay(now.weekday()))