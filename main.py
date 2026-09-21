import os
import re
import yaml
from dotenv import load_dotenv

load_dotenv()

def _substitute_env_vars(value):
    """Replace ${VAR} patterns with environment variable values."""
    if isinstance(value, str):
        return re.sub(
            r'\$\{(\w+)\}',
            lambda m: os.environ.get(m.group(1), m.group(0)),
            value
        )
    if isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_substitute_env_vars(i) for i in value]
    return value

def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        raw = yaml.safe_load(f)
    return _substitute_env_vars(raw)
