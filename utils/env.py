import json
import os
from pathlib import Path


def load_env() -> None:
    env_path = Path(__file__).resolve().parent.parent / "env.json"
    with open(env_path) as f:
        variables = json.load(f)
    for key, value in variables.items():
        os.environ[key] = str(value)
