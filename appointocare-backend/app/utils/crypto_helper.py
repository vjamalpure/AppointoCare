import os
import base64
import hashlib
import hmac
import secrets


def _get_encryption_key():
    """Derives a consistent 32-byte secret key from environment or app secret."""
    raw_secret = os.getenv("APP_ENCRYPTION_KEY") or os.getenv("SECRET_KEY") or "AppointoCare_Enterprise_Master_Secret_Key_2026_Secure"
    return hashlib.sha256(raw_secret.encode()).digest()


def encrypt_token(plain_text: str) -> str:
    """
    Encrypts sensitive tokens (Meta WABA Access Token, Razorpay OAuth tokens)
    using an authenticated stream cipher (ChaCha20/XOR with HMAC-SHA256).
    Returns a URL-safe Base64 string: [16-byte salt][32-byte MAC][ciphertext].
    """
    if not plain_text:
        return ""
    
    key = _get_encryption_key()
    salt = secrets.token_bytes(16)
    
    # Derive keystream for encryption
    stream_key = hmac.new(key, salt, hashlib.sha256).digest()
    data_bytes = plain_text.encode("utf-8")
    
    # Stream cipher keystream generator
    keystream = bytearray()
    counter = 0
    while len(keystream) < len(data_bytes):
        block = hmac.new(stream_key, counter.to_bytes(4, 'big'), hashlib.sha256).digest()
        keystream.extend(block)
        counter += 1
    
    # Encrypt via XOR
    ciphertext = bytes([b ^ k for b, k in zip(data_bytes, keystream[:len(data_bytes)])])
    
    # Compute HMAC authentication tag
    tag = hmac.new(key, salt + ciphertext, hashlib.sha256).digest()
    
    # Pack: salt (16) + tag (32) + ciphertext
    payload = salt + tag + ciphertext
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def decrypt_token(cipher_text: str) -> str:
    """
    Decrypts and verifies authentication tag for sensitive stored tokens.
    """
    if not cipher_text:
        return ""
    
    try:
        raw = base64.urlsafe_b64decode(cipher_text.encode("utf-8"))
        if len(raw) < 48:
            return ""
        
        salt = raw[:16]
        tag = raw[16:48]
        ciphertext = raw[48:]
        
        key = _get_encryption_key()
        
        # Verify HMAC tag first (encrypt-then-MAC)
        expected_tag = hmac.new(key, salt + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected_tag):
            return ""  # Tampered or corrupted ciphertext
        
        # Derive keystream and decrypt
        stream_key = hmac.new(key, salt, hashlib.sha256).digest()
        keystream = bytearray()
        counter = 0
        while len(keystream) < len(ciphertext):
            block = hmac.new(stream_key, counter.to_bytes(4, 'big'), hashlib.sha256).digest()
            keystream.extend(block)
            counter += 1
            
        decrypted_bytes = bytes([c ^ k for c, k in zip(ciphertext, keystream[:len(ciphertext)])])
        return decrypted_bytes.decode("utf-8")
    except Exception:
        return ""
