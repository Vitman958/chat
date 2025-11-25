import os
import hashlib


def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
        dklen=128
    )

    return salt.hex() + ":" + key.hex()


def verify_password(password, stored_hash):
    salt_hex, key_hex = stored_hash.split(":")
    salt = bytes.fromhex(salt_hex)
    key = bytes.fromhex(key_hex)

    new_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000,
        dklen=128
    )

    return new_key == key