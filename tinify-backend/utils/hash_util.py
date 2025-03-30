from hashlib import sha256
import string

# Base 62 chars -- A-Z, a-z, 0-9
BASE62_CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits

def base62_encoding(num):
    if num == 0: return BASE62_CHARS[0]

    base62_str = ""
    while num:
        num, rem = divmod(num, 62)
        base62_str = BASE62_CHARS[rem] + base62_str
    return base62_str

# Hash function to generate a unique ID for a URL
def get_hash(val):
    # Use SHA256 or any other hashing algorithm
    hash_object = sha256(val.encode('utf-8'))
    return int(hash_object.hexdigest(), 16)     # convert hex to int