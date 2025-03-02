import os
import json
from typing import List

def read_existing_json(file_path: str) -> List[dict]:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def write_json(file_path: str, data: List[dict]):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)