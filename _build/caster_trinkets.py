"""Measured pre-raid trinket substitutions for damage casters, by faction and partner."""
import json
from functools import lru_cache
from pathlib import Path


FILE = Path(__file__).with_name("corrections") / "caster_trinkets.json"


@lru_cache(maxsize=1)
def tables():
    """Return the solo and conditional DPS tables in the faction ladder's input format."""
    data = json.loads(FILE.read_text(encoding="utf-8"))
    result = {}
    for profile, record in data["profiles"].items():
        cls, spec = profile.split()
        result[cls, int(spec)] = {"trinket": record["contexts"]}
    return result
