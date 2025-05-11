# backend/crypto.py

import os
import base64
import binascii
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Load a 32-byte key from the environment (base64-encoded)
ENCRYPTION_KEY = base64.b64decode(os.environ['DUNKEY_AES_KEY'])

def encrypt_master(plaintext: str) -> str:
    """
    Encrypts `plaintext` under AES-GCM with a 96-bit nonce.
    Returns a base64-encoded string of nonce‖ciphertext‖tag.
    """
    data = plaintext.encode('utf-8')
    iv = get_random_bytes(12)  # 96-bit nonce
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    token = iv + ciphertext + tag
    return base64.b64encode(token).decode('utf-8')

def decrypt_master(token: str) -> str:
    """
    Decodes the base64 `token` and decrypts under AES-GCM.
    Returns the UTF-8 plaintext or empty string on failure.
    """
    if not token:
        return ''
    # Ensure proper padding
    padding = (-len(token)) % 4
    token += '=' * padding
    try:
        raw = base64.b64decode(token)
        iv, ct_tag = raw[:12], raw[12:]
        ciphertext, tag = ct_tag[:-16], ct_tag[-16:]
        cipher = AES.new(ENCRYPTION_KEY, AES.MODE_GCM, nonce=iv)
        pt = cipher.decrypt_and_verify(ciphertext, tag)
        return pt.decode('utf-8')
    except (binascii.Error, ValueError):
        return ''
