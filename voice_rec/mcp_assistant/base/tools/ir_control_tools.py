from typing import Optional
from .ir_control.tools import (
    list_ir_codes as _list_ir_codes,
    send_ir_by_name as _send_ir_by_name,
    send_ir_by_hex as _send_ir_by_hex,
    learn_ir_and_save as _learn_ir_and_save,
    get_ir_code_info as _get_ir_code_info,
    set_ir_code_info as _set_ir_code_info
)

async def list_ir_codes() -> str:
    """
    List available IR hex files.
    Returns a JSON string containing the list of IR codes.
    """
    return _list_ir_codes({})

async def send_ir_by_name(name: str) -> str:
    """
    Send a saved IR code by name.
    name: The name of the IR code file (without .hex extension).
    """
    return _send_ir_by_name({"name": name})

async def send_ir_by_hex(hex_str: str) -> str:
    """
    Send raw IR hex data.
    hex_str: The hex string of the IR data.
    """
    return _send_ir_by_hex({"hex": hex_str})

async def learn_ir_and_save() -> str:
    """
    Enter IR learning mode and save the received code.
    Returns the path of the saved file.
    """
    return _learn_ir_and_save({})

async def get_ir_code_info(name: str) -> str:
    """
    Get metadata for a specific IR code.
    name: The name of the IR code.
    """
    return _get_ir_code_info({"name": name})

async def set_ir_code_info(name: str, description: Optional[str] = None, aliases: Optional[str] = None, category: Optional[str] = None, device: Optional[str] = None) -> str:
    """
    Set or update metadata for an IR code.
    name: The name of the IR code.
    description: Description of the code.
    aliases: Comma-separated aliases or JSON string array.
    category: Category of the device.
    device: Device name.
    """
    args = {"name": name}
    if description is not None: args["description"] = description
    if aliases is not None: args["aliases"] = aliases
    if category is not None: args["category"] = category
    if device is not None: args["device"] = device
    return _set_ir_code_info(args)
