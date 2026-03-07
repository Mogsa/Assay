import hashlib


def hash_token(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
