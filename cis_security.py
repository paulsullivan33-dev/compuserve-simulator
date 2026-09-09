import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 240_000


def hash_password(password):
    if len(password) < 4:
        raise ValueError("Password must contain at least four characters")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS
    ).hex()
    return f"{ALGORITHM}${ITERATIONS}${salt}${digest}"


def verify_password(password, encoded):
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        ).hex()
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(actual, expected)
