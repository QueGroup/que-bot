import hashlib
import hmac
import secrets
import time
from typing import Any


def generate_signature(telegram_id: int, secret_key: str) -> dict[str, Any]:
    timestamp = int(time.time())
    nonce = secrets.randbits(32) % (999999 - 100000) + 100000
    data_to_sign = f"{telegram_id}{timestamp}{nonce}"

    signature = hmac.new(secret_key.encode(), data_to_sign.encode(), hashlib.sha256).hexdigest()
    return {"telegram_id": telegram_id, "signature": signature, "nonce": nonce, "timestamp": timestamp}
