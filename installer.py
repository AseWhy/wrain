import zipfile
import json
import asyncio
import hashlib
import os.path
from pathlib import Path

PREFIX = "[installer]"
WORKPATH =  str(Path().home()) + "/projects/"
DECODER = json.JSONDecoder()

DEFAULT_PROPERTIES = {}

def checkWidget(widget_dc: dict, prefix: str = "[package-validator]", uid: bool = False):
    if(widget_dc.get("widget") == None or type(widget_dc.get("widget")) != dict):
        print(prefix+" Incorrect widget file formatting")
        return False
    elif(widget_dc.get("widget").get("name") == None or type(widget_dc.get("widget").get("name")) != str):
        print(prefix+" No valid widget name")
        return False
    elif(widget_dc.get("widget").get("version") == None or type(widget_dc.get("package").get("version")) != float):
        print(prefix+" No valid package version")
        return False
    elif(uid == True):
        if(widget_dc.get("uid") == None or type(widget_dc.get("uid")) != str):
            print(prefix+" There is no unique identifier")
            return False
    return True

def checkPackage(package_dc: dict, prefix: str = "[package-validator]", uid: bool = False):
    if(package_dc.get("package") == None or type(package_dc.get("package")) != dict):
        print(prefix+" Incorrect package file formatting")
        return False
    elif(package_dc.get("package").get("name") == None or type(package_dc.get("package").get("name")) != str):
        print(prefix+" No valid package name")
        return False
    elif(package_dc.get("package").get("version") == None or type(package_dc.get("package").get("version")) != float):
        print(prefix+" No valid package version")
        return False
    elif(uid == True):
        if(package_dc.get("uid") == None or type(package_dc.get("uid")) != str):
            print(prefix+" There is no unique identifier")
            return False
    return True

def read(zipfile, name):
    try:
        with zipfile.open(name, "r") as f:
            return f.read().decode('utf-8')
    except:
        print("[installer] Unable to find address " + name)
        return None
def getUID():
    c_file = WORKPATH + ".wrain_cache"
    last = 0
    if(os.path.exists(c_file)):
        with open(c_file, "r") as f:
            last = int(f.read())
            last += 1

    with open(c_file, "w") as w:
        w.write(str(last))
    
    hash = hashlib.sha256(str(last).encode('utf-8')).hexdigest()

    return str(hash[0:15]+"-"+hash[15:45]+"-"+hash[45:])
async def install(path, state, delete_on_end = False):
    if(not os.path.exists(WORKPATH)):
        os.makedirs(WORKPATH)

    if(zipfile.is_zipfile(path)):
        state(PREFIX + " Unpacking "+path)
        with zipfile.ZipFile(path) as zip:
            PRFOLDER = WORKPATH + getUID() + "/"
            state(PREFIX + " Processing project.json file")
            project_config = json.loads(read(zip, "project.json"))

            if(checkPackage(project_config) == False):
                state(PREFIX + " Invalid project file")
                raise Exception(PREFIX + " Invalid project file")

            project_config["widgets"] = []
            project_config["uid"] = str(getUID())
            widgets = []

            state(PREFIX + " Processing widget files:")

            locale = read(zip, "localisation.json")

            if(locale == None):
                state(PREFIX + " Invalid localisation file")
                raise Exception(PREFIX + " Invalid localisation file")
            else:
                locale = DECODER.decode(locale)

            for info in zip.infolist():
                if(info.is_dir() and info.filename != "__pycache__"):
                    state(PREFIX + " Processing "+info.filename)

                    w_config = read(zip, info.filename + "widget.json")

                    if(w_config != None):
                        config = DECODER.decode(w_config)

                        if(config.get("widget") != None):
                            drawer = None

                            if(config.get("widget").get("drawer") != None):
                                drawer = read(zip, info.filename + config.get("widget").get("drawer"))
                            else:
                                drawer = read(zip, info.filename + "drawer.py")


                            if(drawer == None):
                                #Drawer not found [Exit]
                                state(PREFIX + " Invalid render file")
                                raise Exception(PREFIX + " Invalid render file")

                            config["uid"] = str(getUID())
                            widgets.append([config, drawer])
                        else:
                            #Exit
                            state(PREFIX + " Invalid widget file")
                            raise Exception(PREFIX + " Invalid widget file")

            
            os.makedirs(PRFOLDER)
            state(PREFIX + " Create project directory " + PRFOLDER)

            wid = 0
            for widget in widgets:
                state(PREFIX+" Writing "+str(wid))
                widget[0]["widget"]["drawer"] = str(wid) + ".py"

                with open(PRFOLDER + str(wid) + ".json", "w") as w:
                    w.write(json.dumps(widget[0]))

                with open(PRFOLDER + str(wid) + ".py", "w") as w:
                    w.write(widget[1])

                project_config["widgets"].append(wid)
                wid += 1

            state(PREFIX + " Writing " + PRFOLDER + "project.json")

            with open(PRFOLDER + "project.json", "w") as w:
                w.write(json.dumps(project_config))

            with open(PRFOLDER + "localisation.json", "w") as w:
                w.write(json.dumps(locale))

            with open(PRFOLDER + "properties.json", "w") as w:
                w.write(json.dumps(DEFAULT_PROPERTIES))

            if(delete_on_end):
                state(PREFIX + " Remove "+path)
                os.remove(path)

            state(PREFIX + " Instalation done")