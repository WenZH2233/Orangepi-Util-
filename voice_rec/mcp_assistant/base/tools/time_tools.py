import datetime

def get_current_time() -> dict:
    """Get the current system time. Use this tool when asked about the current time or date."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"success": True, "result": f"Current time is: {now}"}
