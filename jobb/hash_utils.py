import hashlib
import os

def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16).hex()  # Generate a new 16-byte salt
    salted_password = password + salt
    hashed = hashlib.md5(salted_password.encode()).hexdigest()
    return hashed, salt
