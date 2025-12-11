import platform
import subprocess
import socket
import os
import logging

logger = logging.getLogger("Tools.SystemInfo")

def _run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return "N/A"

def get_system_info() -> dict:
    """
    Get comprehensive system information including OS, CPU, Memory, Disk, Network, and Temperature.
    Use this tool when asked about system status, specs, hardware info or health.
    """
    info = {}
    
    # OS Info
    info['os'] = platform.platform()
    info['hostname'] = socket.gethostname()
    info['python_version'] = platform.python_version()
    
    # CPU Info
    try:
        # Try to get CPU model
        cpu_model = _run_cmd("cat /proc/cpuinfo | grep 'model name' | head -n 1")
        if not cpu_model:
             cpu_model = _run_cmd("lscpu | grep 'Model name'")
        
        # Clean up the string
        if ":" in cpu_model:
            cpu_model = cpu_model.split(":", 1)[1].strip()
            
        info['cpu_model'] = cpu_model or platform.processor()
        info['cpu_count'] = os.cpu_count()
        
        # CPU Load
        load_avg = os.getloadavg()
        info['load_average'] = {
            '1min': load_avg[0],
            '5min': load_avg[1],
            '15min': load_avg[2]
        }
    except Exception as e:
        logger.error(f"Error getting CPU info: {e}")

    # Memory Info
    try:
        # Parse /proc/meminfo for more accurate raw data if needed, but free is easier for human readable
        mem_total = _run_cmd("free -h | awk '/^Mem:/ {print $2}'")
        mem_used = _run_cmd("free -h | awk '/^Mem:/ {print $3}'")
        mem_free = _run_cmd("free -h | awk '/^Mem:/ {print $4}'")
        mem_available = _run_cmd("free -h | awk '/^Mem:/ {print $7}'")
        
        info['memory'] = {
            'total': mem_total,
            'used': mem_used,
            'free': mem_free,
            'available': mem_available
        }
    except Exception:
        pass

    # Disk Info (Root partition)
    try:
        disk_usage = _run_cmd("df -h / | awk 'NR==2 {print $2, $3, $4, $5}'").split()
        if len(disk_usage) >= 4:
            info['disk_root'] = {
                'total': disk_usage[0],
                'used': disk_usage[1],
                'free': disk_usage[2],
                'percent': disk_usage[3]
            }
    except Exception:
        pass

    # Network Info
    try:
        # Get primary IP
        ip = _run_cmd("hostname -I").split()
        info['ip_addresses'] = ip
    except Exception:
        pass

    # Uptime
    info['uptime'] = _run_cmd("uptime -p")

    # Temperature (Common paths for Linux/OrangePi/RaspberryPi)
    try:
        temp_paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/hwmon/hwmon0/temp1_input"
        ]
        
        for path in temp_paths:
            if os.path.exists(path):
                temp_raw = _run_cmd(f"cat {path}")
                if temp_raw.isdigit():
                    info['cpu_temperature'] = f"{int(temp_raw) / 1000:.1f}°C"
                    break
    except Exception:
        pass

    return {"success": True, "result": info}
