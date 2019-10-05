import re

class Color:
    Opacity = 1
    Color = 0x000000

    def __init__(self, color, opacity):
        self.Opacity = opacity
        self.Color = color

def parser(string):
    if(string[0:4] == "rgba"):
        math = re.search("rgba\( *(\d+\.?\d*?) *, *(\d+\.?\d*?) *, *(\d+\.?\d*?) *, *(\d+\.?\d*?) *\)", string)
        return Color(int(hex(int(math[1]))[2:]+ hex(int(math[2]))[2:]+ hex(int(math[3]))[2:], 16), float(math[4]))
    if(string[0:3] == "rgb"):
        math = re.search("rgba\( *(\d+\.?\d*?) *, *(\d+\.?\d*?) *, *(\d+\.?\d*?) *\)", string)
        return Color(int(hex(int(math[1]))[2:]+ hex(int(math[2]))[2:]+ hex(int(math[3]))[2:], 16), 1)
    if(string[1] == "#"):
        return Color(int(math[1:6], 16), 1)