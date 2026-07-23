from otp_utils import *

otp = generate_otp()

print("OTP:", otp)

otp_hash, salt = hash_otp_for_storage(otp)

print("Hash:", otp_hash)
print("Salt:", salt)

print("Correct:", verify_otp(otp, otp_hash, salt))
print("Wrong:", verify_otp("123456", otp_hash, salt))