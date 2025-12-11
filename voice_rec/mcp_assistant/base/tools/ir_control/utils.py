import logging
import os
from pathlib import Path

def get_logger(name):
    return logging.getLogger(name)

def get_ir_data_dir():
    # Use a local data directory for IR codes
    path = Path(os.getcwd()) / "data" / "ir_codes"
    os.makedirs(path, exist_ok=True)
    return str(path)
