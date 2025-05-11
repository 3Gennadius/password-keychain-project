import base64, os

key = os.urandom(32)               # 32 random bytes
b64 = base64.b64encode(key).decode()
print(b64)