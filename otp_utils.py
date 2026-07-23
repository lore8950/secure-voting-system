import random
import hashlib
import secrets


def generate_otp() -> str:
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))


def hash_otp_for_storage(otp: str):
    """Return (otp_hash, salt) for database storage."""
    salt = secrets.token_hex(16)

    otp_hash = hashlib.sha256(
        (otp + salt).encode("utf-8")
    ).hexdigest()

    return otp_hash, salt


def verify_otp(user_otp: str, otp_hash: str, salt: str) -> bool:
    """Verify user OTP."""
    check = hashlib.sha256(
        (user_otp + salt).encode("utf-8")
    ).hexdigest()

    return check == otp_hash