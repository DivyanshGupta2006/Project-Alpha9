import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# OPTIMIZED
def check(directory):
    os.makedirs(directory, exist_ok=True)

# OPTIMIZED
def absolute(path):
    return PROJECT_ROOT.joinpath(path)
