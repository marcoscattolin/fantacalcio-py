# config.py
import os
import base64

import src


def decode(stringa):
    return base64.b64decode(stringa).decode("utf-8")


# PATHS
ROOT_DIR = os.path.dirname(os.path.dirname(src.__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
TEMP_DIR = os.path.join(DATA_DIR, "temp")
