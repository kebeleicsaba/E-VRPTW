import numpy as np
import json
from pathlib import Path

def to_python_type(obj):
    """Recursively convert numpy types to python built-ins for JSON serialization."""
    if isinstance(obj, dict):
        return {k: to_python_type(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_python_type(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def save_log(log_path, log_data):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    py_data = to_python_type(log_data)
    with open(log_path, "w") as f:
        json.dump(py_data, f, indent=2)
