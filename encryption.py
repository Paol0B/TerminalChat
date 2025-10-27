"""
Secure Encryption Module for Terminal Chat
Implements hybrid encryption using RSA for key exchange and AES for message encryption.
All operations are performed in memory with no disk persistence.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class SecureEncryption:
    """
    Handles end-to-end encryption using RSA + AES hybrid approach.
    - RSA for secure key exchange
    - AES-256 for fast message encryption
    - All keys stored only in memory
    """
    
    def __init__(self):
        """Initialize encryption with new RSA key pair."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.peer_public_key = None
        self.session_key = None
    
    def get_public_key_bytes(self):
        """
        Export public key as bytes for transmission.
        Returns: bytes - serialized public key
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def set_peer_public_key(self, peer_key_bytes):
        """
        Import peer's public key from bytes.
        Args:
            peer_key_bytes: bytes - serialized public key from peer
        """
        self.peer_public_key = serialization.load_pem_public_key(
            peer_key_bytes,
            backend=default_backend()
        )
    
    def generate_session_key(self):
        """
        Generate a new AES session key (256-bit).
        Returns: bytes - 32-byte session key
        """
        self.session_key = os.urandom(32)
        return self.session_key
    
    def encrypt_session_key(self, session_key=None):
        """
        Encrypt session key with peer's public RSA key.
        Args:
            session_key: bytes - key to encrypt (uses self.session_key if None)
        Returns: bytes - encrypted session key
        """
        if session_key is None:
            session_key = self.session_key
        
        if self.peer_public_key is None:
            raise ValueError("Peer public key not set")
        
        encrypted_key = self.peer_public_key.encrypt(
            session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_key
    
    def decrypt_session_key(self, encrypted_key):
        """
        Decrypt session key using own private RSA key.
        Args:
            encrypted_key: bytes - encrypted session key
        Returns: bytes - decrypted session key
        """
        session_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        self.session_key = session_key
        return session_key
    
    def encrypt_message(self, message, session_key=None):
        """
        Encrypt message using AES-256-GCM.
        Args:
            message: str or bytes - message to encrypt
            session_key: bytes - encryption key (uses self.session_key if None)
        Returns: tuple - (iv, ciphertext, tag)
        """
        if session_key is None:
            session_key = self.session_key
        
        if session_key is None:
            raise ValueError("Session key not set")
        
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Generate random IV (initialization vector)
        iv = os.urandom(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(session_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt message
        ciphertext = encryptor.update(message) + encryptor.finalize()
        
        return iv, ciphertext, encryptor.tag
    
    def decrypt_message(self, iv, ciphertext, tag, session_key=None):
        """
        Decrypt message using AES-256-GCM.
        Args:
            iv: bytes - initialization vector
            ciphertext: bytes - encrypted message
            tag: bytes - authentication tag
            session_key: bytes - decryption key (uses self.session_key if None)
        Returns: str - decrypted message
        """
        if session_key is None:
            session_key = self.session_key
        
        if session_key is None:
            raise ValueError("Session key not set")
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(session_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt message
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext.decode('utf-8')
    
    def clear_keys(self):
        """
        Securely clear all keys from memory.
        Called on exit to ensure no key persistence.
        """
        self.private_key = None
        self.public_key = None
        self.peer_public_key = None
        self.session_key = None
