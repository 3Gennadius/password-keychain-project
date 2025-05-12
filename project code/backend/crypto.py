import os
import base64
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Load environment variables from .env (if present)
load_dotenv()

# Load and validate encryption key
_key_b64 = os.getenv('DUNKEY_AES_KEY')
if not _key_b64:
    raise RuntimeError(
        "Environment variable DUNKEY_AES_KEY is not set. "
        "Please define it in your .env or environment."
    )

try:
    ENCRYPTION_KEY = base64.b64decode(_key_b64)
except Exception as e:
    raise RuntimeError(f"Failed to base64-decode DUNKEY_AES_KEY: {e}")

# AES block size (16 bytes)
BLOCK_SIZE = AES.block_size

def encrypt_master(plaintext: str) -> bytes:
    """
    Encrypts plaintext with AES-CBC using the ENV key.
    Returns IV + ciphertext bytes.
    """
    iv = os.urandom(BLOCK_SIZE)
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(plaintext.encode('utf-8'), BLOCK_SIZE))
    return iv + ct

def decrypt_master(ciphertext: bytes) -> str:
    """
    Decrypts data produced by encrypt_master.
    Expects IV (first BLOCK_SIZE bytes) + ciphertext.
    Returns the original plaintext string.
    """
    iv = ciphertext[:BLOCK_SIZE]
    ct = ciphertext[BLOCK_SIZE:]
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), BLOCK_SIZE)
    return pt.decode('utf-8')
