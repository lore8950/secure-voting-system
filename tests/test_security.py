from security_utils import (
    hash_password,
    verify_password,
    hash_otp,
    verify_otp_hash,
)

password = "Admin123"
hashed_password = hash_password(password)

print("Password Hash:", hashed_password)
print("Password OK:", verify_password(password, hashed_password))

otp = "123456"
hashed_otp = hash_otp(otp)

print("OTP Hash:", hashed_otp)
print("OTP OK:", verify_otp_hash(otp, hashed_otp))