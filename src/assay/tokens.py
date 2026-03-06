import hashlib
import secrets
import string


def hash_token(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def new_opaque_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    return token, hash_token(token)


def new_user_code(length: int = 8) -> tuple[str, str]:
    alphabet = string.ascii_uppercase + string.digits
    raw = "".join(secrets.choice(alphabet) for _ in range(length))
    if length > 4:
        raw = f"{raw[:4]}-{raw[4:]}"
    return raw, hash_token(raw)
