#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

from pathlib import Path
import sys
import json
import os
import main_window
from PyQt5.QtWidgets import QApplication, QMainWindow


if(len(sys.argv) > 1 and "-r" == sys.argv[1]):
    os.system("python3.6 " + str(Path(__file__).resolve().parent) + "/runner.py " + sys.argv[2])
    sys.exit(0)


if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

import installer

CONFIG = str(Path(__file__).resolve().parent)+"/data/config.json"

decode_s = json.JSONDecoder().decode(open(CONFIG, 'r').read())

if(decode_s.get("local") != None):
    if(decode_s.get("local") == "RU_ru"):
        main_window.LOCALe = "RU_ru"
    if(decode_s.get("local") == "EN_us"):
        main_window.LOCALe = "EN_us"
main_window.LoadLocale()

mv = main_window.WorkWindow(decode_s)

if(decode_s.get("show_on_start") == True):
    mv.show()

sys.exit(app.exec_())