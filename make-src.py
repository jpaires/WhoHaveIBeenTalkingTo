import os
import shutil

PYTHON_PATH = "python"

DIRS = ['libs', 'theme', 'cherrypy', 'services']
FILES = ['server.py']
SRC_PATH = "src"

os.system('%s clear.py' % PYTHON_PATH)

for directory in DIRS:
    shutil.copytree(directory, SRC_PATH + "\\" + directory)

for file_ in FILES:
    shutil.copyfile(file_, SRC_PATH + "\\" + file_)
