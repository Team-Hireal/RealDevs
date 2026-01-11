"""Tests for encryption utilities."""
import pytest
from app.utils.encryption import TokenEncryption


def test_encrypt_decrypt():
    """Test encryption and decryption."""
    encryption = TokenEncryption("test-secret-key-12345")
    
    plaintext = "ghp_test_token_12345"
    encrypted = encryption.encrypt(plaintext)
    
    assert encrypted != plaintext
    assert len(encrypted) > 0
    
    decrypted = encryption.decrypt(encrypted)
    assert decrypted == plaintext


def test_different_keys_produce_different_ciphertexts():
    """Test that different keys produce different encrypted outputs."""
    plaintext = "ghp_test_token"
    
    enc1 = TokenEncryption("key1")
    enc2 = TokenEncryption("key2")
    
    encrypted1 = enc1.encrypt(plaintext)
    encrypted2 = enc2.encrypt(plaintext)
    
    assert encrypted1 != encrypted2

