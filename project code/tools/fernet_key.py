import secrets

def generate_secret_key(length_bytes: int = 32) -> str:

    return secrets.token_hex(length_bytes)

if __name__ == "__main__":
    key = generate_secret_key()
    print(key)
