
import sys
import os
import time
import json
import threading

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.ir_control.tools import learn_ir_and_save, get_learning_result

def test_background_learning():
    print("Starting background learning...")
    res = learn_ir_and_save({})
    print(f"Start result: {res}")
    
    for i in range(5):
        time.sleep(1)
        status = get_learning_result({})
        print(f"Status {i}: {status}")
        
        s = json.loads(status)
        if s["status"] == "error":
            print("Error detected!")
            break

if __name__ == "__main__":
    test_background_learning()
