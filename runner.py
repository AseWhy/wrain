import sys
import os
import json
import widget as wd
import uuid
from settings import *
from PyQt5.QtWidgets import QApplication

class mw:
    def show(self):
        print("-1")

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

WORKPATH = sys.argv[1]
WORKPATH = WORKPATH if WORKPATH[len(WORKPATH) - 1] == "/" or WORKPATH[len(WORKPATH) - 1] == "\\" else WORKPATH + "/"
WIDGET = WORKPATH + "widget.json"
DRAWER = WORKPATH + "drawer.py"

decode_s = None

with open(WIDGET, "r") as widget:
    decode_s = json.loads(widget.read())
    if("widget" in decode_s):
        DRAWER = WORKPATH + decode_s["widget"]["drawer"]

if(os.path.exists(DRAWER)):
    wd.Widget(decode_s.get("widget"), DRAWER, "drawer", Settings(400, 400, "Runner", decode_s["widget"].get("origin")), mw(), "test-" + str(uuid.uuid4()))
else:
    raise Exception("Missing drawer file! " + DRAWER)

sys.exit(app.exec_())