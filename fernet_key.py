#Using this for testing purposes, will be deleted in final version
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key.decode())
