import base64
import json
from datetime import datetime


def encode_cursor(data: dict) -> str:
    serializable = {}
    for k, v in data.items():
        if isinstance(v, datetime):
            serializable[k] = v.isoformat()
        else:
            serializable[k] = str(v)
    return base64.urlsafe_b64encode(json.dumps(serializable).encode()).decode()


def decode_cursor(cursor: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(cursor.encode()))
