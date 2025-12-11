import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("Tools.Temperature")

DATA_PATH = Path("/var/lib/temperature_humidity.json")

def _load_data(path: Path) -> dict:
    """Load and validate the temperature/humidity JSON payload."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Expected a file but found a directory: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError("JSON payload must be an object")

    return data

def get_temperature_humidity(file_path: str | None = None) -> dict:
    """Read temperature/humidity from JSON. Optional `file_path` overrides the default location."""
    path = Path(file_path) if file_path else DATA_PATH

    try:
        payload = _load_data(path)
        timestamp = payload.get("timestamp")
        timestamp_iso = None
        if isinstance(timestamp, (int, float)):
            timestamp_iso = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

        result = {
            "success": True,
            "temperature": payload.get("temperature"),
            "humidity": payload.get("humidity"),
            "unit": payload.get("unit"),
            "timestamp": timestamp,
            "timestamp_iso": timestamp_iso,
        }

        logger.info("Loaded temperature/humidity from %s", path)
        return result
    except Exception as exc:
        logger.exception("Failed to load temperature/humidity from %s", path)
        return {"success": False, "error": str(exc)}
