#!/usr/bin/env python3
import sys
import os
import json
import time

# Add the current directory to sys.path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from tools.ir_control.tools import (
        list_ir_codes,
        send_ir_by_name,
        send_ir_by_hex,
        learn_ir_and_save,
        test_ir_connection,
        set_ir_code_info
    )
except ImportError as e:
    print(f"Error importing IR tools: {e}")
    print("Please run this script from 'voice_rec/mcp_assistant/base/' directory.")
    sys.exit(1)

def print_menu():
    print("\n--- IR Control Manual Tool ---")
    print("1. Test Connection")
    print("2. List Available Codes")
    print("3. Send Code by Name")
    print("4. Send Code by Hex")
    print("5. Learn New Code")
    print("0. Exit")
    print("------------------------------")

def handle_list():
    result_json = list_ir_codes({})
    try:
        result = json.loads(result_json)
        if "error" in result:
            print(f"Error: {result['error']}")
            return

        items = result.get("items", [])
        if not items:
            print("No IR codes found.")
        else:
            print(f"\nFound {len(items)} codes:")
            # Sort by name
            items.sort(key=lambda x: x['name'])
            for item in items:
                desc = item.get('description', '')
                aliases = item.get('aliases', [])
                alias_str = f" (Aliases: {', '.join(aliases)})" if aliases else ""
                print(f" - {item['name']}: {desc}{alias_str}")
    except json.JSONDecodeError:
        print(f"Raw output: {result_json}")

def handle_send_name():
    name = input("Enter code name (e.g., tv_power): ").strip()
    if not name:
        return
    try:
        print(f"Sending '{name}'...")
        result = send_ir_by_name({"name": name})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

def handle_send_hex():
    hex_str = input("Enter hex string: ").strip()
    if not hex_str:
        return
    try:
        print("Sending hex...")
        result = send_ir_by_hex({"hex": hex_str})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

def handle_learn():
    print("Entering learning mode. Please point the remote at the receiver and press a button.")
    try:
        result_json = learn_ir_and_save({})
        try:
            result = json.loads(result_json)
            saved_path = result.get("saved")
            print(f"Success! Saved to: {saved_path}")
            
            # Extract filename without extension
            filename = os.path.basename(saved_path)
            name = os.path.splitext(filename)[0]
            
            # Ask to rename/set info
            new_name = input(f"Current name is '{name}'. Enter new name (or press Enter to keep): ").strip()
            if new_name:
                # Rename file
                dirname = os.path.dirname(saved_path)
                new_path = os.path.join(dirname, f"{new_name}.hex")
                try:
                    os.rename(saved_path, new_path)
                    name = new_name
                    print(f"Renamed to: {name}")
                except OSError as e:
                    print(f"Rename failed: {e}")
            
            desc = input("Enter description (optional): ").strip()
            if desc:
                set_ir_code_info({"name": name, "description": desc})
                print("Description updated.")
                
        except json.JSONDecodeError:
             print(f"Result: {result_json}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            print(test_ir_connection({}))
        elif choice == "2":
            handle_list()
        elif choice == "3":
            handle_send_name()
        elif choice == "4":
            handle_send_hex()
        elif choice == "5":
            handle_learn()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
