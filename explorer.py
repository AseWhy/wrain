import subprocess
import sys

print("Init platform: "+sys.platform)

if sys.platform == 'darwin':
    def openFolder(path):
        subprocess.check_call(['open', path])
elif sys.platform == 'linux':
    def openFolder(path):
        subprocess.check_call(['xdg-open', path])
elif sys.platform == 'win32' or sys.platform == "cygwin":
    def openFolder(path):
        subprocess.check_call(['explorer', path])