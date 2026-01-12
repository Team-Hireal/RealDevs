"""Encryption utilities for secure PAT storage."""
# https://github.com/SimonSaysGiveMeSmile
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import hashlib


class TokenEncryption:
    """Handles encryption/decryption of GitHub PAT."""
    
    def __init__(self, secret_key: str):
        """Initialize with secret key from environment."""
        # Derive a valid Fernet key from the secret
        key_bytes = hashlib.sha256(secret_key.encode()).digest()
        self.fernet = Fernet(urlsafe_b64encode(key_bytes))
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext token."""
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt an encrypted token."""
        decrypted = self.fernet.decrypt(encrypted_text.encode())
        return decrypted.decode()

