import logging
import os
from pathlib import Path

def get_logger(name):
    return logging.getLogger(name)

def get_user_data_dir():
    # Use a local data directory
    path = Path(os.getcwd()) / "data"
    os.makedirs(path, exist_ok=True)
    return path
