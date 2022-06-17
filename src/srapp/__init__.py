# -----------------------------------------------------------
# Copyright (C) 2022 Wojciech Szpikowski
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# ---------------------------------------------------------------------
import os
import subprocess
import sys

# add paths for QGIS
srapp_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(srapp_path)
srapp_model_path = os.path.join(srapp_path, 'srapp_model')
sys.path.append(srapp_model_path)

try:
    import firebase_admin
except:
    py_path = sys.executable
    # Windows QGiS specific
    if 'qgis-bin.exe' in py_path:
        osgeo4w_path = os.path.dirname(os.path.dirname(py_path))
        py_path = os.path.join(osgeo4w_path, 'apps', 'Python39', 'python.exe')
    # install firebase_admin
    subprocess.check_call([py_path, "-m", "pip", "install", "firebase_admin"])

from srapp.plugin import SrappPlugin


def classFactory(iface):
    return SrappPlugin(iface)
