import os
import shutil

PYTHON_PATH = 'python'

DIST_PATH = 'dist'
DEPENDENCES_PATHS = ['theme', 'libs']
BUILD_PATH = 'build'

os.system('%s setup.py py2exe' % PYTHON_PATH)

for dependence in DEPENDENCES_PATHS:
    shutil.copytree(dependence, DIST_PATH + "\\" + dependence)
shutil.rmtree(BUILD_PATH)
