import os

os.environ["ADMIN_PASSWORD"] = "test-admin-password"

from security_utils import verify_admin_password

assert verify_admin_password("test-admin-password")
assert not verify_admin_password("wrong-password")
