from fastmcp import FastMCP
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AllTools')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

# Import tools
from tools.math_tools import calculator
from tools.time_tools import get_current_time
from tools.temperature_tools import get_temperature_humidity
from tools.system_tools import set_volume, get_volume, launch_application
from tools.system_info_tools import get_system_info
from tools.calendar_tools import (
    create_event,
    get_events_by_date,
    update_event,
    delete_event,
    delete_events_batch,
    get_categories,
    get_upcoming_events
)
from tools.ir_control_tools import (
    list_ir_codes,
    send_ir_by_name,
    send_ir_by_hex,
    learn_ir_and_save,
    get_ir_code_info,
    set_ir_code_info
)

# Create an MCP server
mcp = FastMCP("AllTools")

# Register tools
# The mcp.tool() decorator can be used as a function call to register existing functions
mcp.tool()(calculator)
mcp.tool()(get_current_time)
mcp.tool()(get_temperature_humidity)
mcp.tool()(set_volume)
mcp.tool()(get_volume)
mcp.tool()(launch_application)
mcp.tool()(get_system_info)
mcp.tool()(create_event)
mcp.tool()(get_events_by_date)
mcp.tool()(update_event)
mcp.tool()(delete_event)
mcp.tool()(delete_events_batch)
mcp.tool()(get_categories)
mcp.tool()(get_upcoming_events)
mcp.tool()(list_ir_codes)
mcp.tool()(send_ir_by_name)
mcp.tool()(send_ir_by_hex)
mcp.tool()(learn_ir_and_save)
mcp.tool()(get_ir_code_info)
mcp.tool()(set_ir_code_info)

# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
