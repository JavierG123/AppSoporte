import json
from pathlib import Path
from typing import Any, Dict, Iterable

REQUIRED_CONFIG_KEYS = (
    "icon",
    "programsFolder",
    "genesysToolsFolder",
)


def _missing_keys(config: Dict[str, Any], required_keys: Iterable[str]) -> list[str]:
    return [key for key in required_keys if key not in config]


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate required AppSoporte configuration keys."""
    with open(config_path, encoding="utf-8") as config_file:
        config: Dict[str, Any] = json.load(config_file)

    missing = _missing_keys(config, REQUIRED_CONFIG_KEYS)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Missing required config keys: {joined}")

    return config
