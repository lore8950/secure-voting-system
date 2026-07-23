import bcrypt
import hmac
import os
import re

# ==========================
# Admin Password
# ==========================

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# ==========================
# Password Functions
# ==========================

def hash_password(password: str) -> str:
    """Hash a password before storing in the database."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against stored hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

# ==========================
# Admin Verification
# ==========================

def verify_admin_password(password: str) -> bool:
    """Verify admin password."""
    return bool(ADMIN_PASSWORD) and hmac.compare_digest(password, ADMIN_PASSWORD)


def is_strong_password(password: str) -> bool:
    """
    Password must contain:
    - At least 8 characters
    - One uppercase letter
    - One lowercase letter
    - One number
    - One special character
    """

    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$"

    return re.match(pattern, password) is not None
