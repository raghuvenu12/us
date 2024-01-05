import string, random, hashlib


def otp6():
    return random.randint(100000, 999999)


def token_alphanum(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for x in range(size))


def token_alphanum8():
    return token_alphanum(8)


def token_alphanum16():
    return token_alphanum(16)


def token_alphanum36():
    return token_alphanum(36)


def create_hash(token: str):
    salt = 'ps:'
    token = (salt+token).encode('utf-8')
    return hashlib.md5(token).hexdigest()




# import hashlib

# def create_hash(token: str):
#     # Use a strong hashing algorithm, such as SHA-256
#     # You should also use a salt, which adds randomness to the hash to enhance security
#     salt = 'your_salt_here'
#     token = (salt + token).encode('utf-8')
#     return hashlib.sha256(token).hexdigest()
