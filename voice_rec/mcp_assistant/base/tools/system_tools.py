import subprocess
import logging
import shutil

logger = logging.getLogger("Tools.System")

def _run_command(command: list[str]) -> str:
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        raise e

def set_volume(volume: int) -> dict:
    """
    Set the system volume (0-100).
    Use this tool when the user wants to adjust the volume.
    """
    if not (0 <= volume <= 100):
        return {"success": False, "error": "Volume must be between 0 and 100"}

    try:
        # Try using amixer (ALSA) which is common on Linux/OrangePi
        # This might need adjustment based on the specific sound card or mixer control name (e.g., 'Master', 'PCM', 'Line Out')
        # Trying 'Master' first, then 'PCM'
        controls = ['Master', 'PCM', 'Speaker', 'Headphone']
        success = False
        
        for control in controls:
            try:
                _run_command(["amixer", "set", control, f"{volume}%"])
                success = True
                break
            except Exception:
                continue
        
        if success:
            return {"success": True, "result": f"Volume set to {volume}%"}
        else:
            return {"success": False, "error": "Could not find a suitable mixer control (Master/PCM/Speaker)"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_volume() -> dict:
    """
    Get the current system volume.
    """
    try:
        # Simple parsing of amixer output
        # Output format example: ... [50%] ...
        controls = ['Master', 'PCM', 'Speaker', 'Headphone']
        output = ""
        
        for control in controls:
            try:
                output = _run_command(["amixer", "get", control])
                break
            except Exception:
                continue
        
        if not output:
             return {"success": False, "error": "Could not get volume info"}

        import re
        match = re.search(r"\[(\d+)%\]", output)
        if match:
            return {"success": True, "result": int(match.group(1))}
        else:
            return {"success": False, "error": "Could not parse volume from output"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def launch_application(app_name: str) -> dict:
    """
    Launch an application by name or command.
    Example: 'firefox', 'chromium', 'vlc'
    """
    # Security note: Be careful with executing arbitrary commands. 
    # Here we assume app_name is a simple command.
    
    # Check if command exists
    if not shutil.which(app_name):
         return {"success": False, "error": f"Application '{app_name}' not found in PATH"}

    try:
        # Run in background
        subprocess.Popen([app_name], start_new_session=True)
        return {"success": True, "result": f"Launched {app_name}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
