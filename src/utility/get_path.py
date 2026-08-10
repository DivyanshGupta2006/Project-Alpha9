import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def check(directory):
    os.makedirs(directory, exist_ok=True)

def absolute(path):
    return PROJECT_ROOT.joinpath(path)