class Settings:
    defaultWidth = 400
    defaultHeight = 400
    projectName = None
    origin = 0

    def __init__(self, dw, dh, pn, org = None):
        if(dh != None):
            self.defaultHeight = dh
        if(dw != None):
            self.defaultWidth = dw
        if(pn != None):
            self.projectName = pn

        if(org == None):
            self.origin = 0
        elif(org.lower() == "upper-right"):
            self.origin = 0
        elif(org.lower() == "middle-right"):
            self.origin = 1
        elif(org.lower() == "lower-right"):
            self.origin = 2
        elif(org.lower() == "upper-center"):
            self.origin = 3
        elif(org.lower() == "middle-center"):
            self.origin = 4
        elif(org.lower() == "lower-center"):
            self.origin = 5
        elif(org.lower() == "upper-left"):
            self.origin = 6
        elif(org.lower() == "middle-left"):
            self.origin = 7
        elif(org.lower() == "lower-left"):
            self.origin = 8