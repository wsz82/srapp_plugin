# -----------------------------------------------------------
# Copyright (C) 2022 Wojciech Szpikowski
# -----------------------------------------------------------
# Licensed under the terms of GNU GPL 3
# ---------------------------------------------------------------------
import os
import subprocess
import sys

# add paths for QGIS
srapp_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(srapp_path)
srapp_model_path = os.path.join(srapp_path, 'srapp_model')
sys.path.append(srapp_model_path)


def find_python():
    if sys.platform != "win32":
        return sys.executable

    for path in sys.path:
        assumed_path = os.path.join(path, "python.exe")
        if os.path.isfile(assumed_path):
            return assumed_path

    return None


try:
    import firebase_admin
except:
    py_path = find_python()
    # install firebase_admin
    if py_path:
        subprocess.check_call([py_path, "-m", "pip", "install", "firebase_admin"])

from srapp.plugin import SrappPlugin


def classFactory(iface):
    return SrappPlugin(iface)
