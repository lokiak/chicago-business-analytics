"""
Secure storage utilities for sensitive data
Provides encryption/decryption for local data files
"""

import os
import json
import pickle
import hashlib
from typing import Any, Dict, Optional, Union
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from security_utils import SecurityLogger


class SecureStorage:
    """Handles encryption/decryption of sensitive local data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize secure storage
        
        Args:
            encryption_key: Base64 encoded encryption key. If None, will try to get from environment
        """
        self.encryption_key = encryption_key or os.getenv('DATA_ENCRYPTION_KEY')
        self.cipher_suite = None
        
        if self.encryption_key:
            try:
                # The key should already be base64 encoded
                self.cipher_suite = Fernet(self.encryption_key.encode())
                SecurityLogger.log_security_event("encryption_initialized", "Data encryption enabled")
            except Exception as e:
                SecurityLogger.log_security_event("encryption_init_failed", f"Failed to initialize encryption: {e}", "ERROR")
                self.cipher_suite = None
        else:
            SecurityLogger.log_security_event("encryption_disabled", "No encryption key provided - data will be stored unencrypted", "WARNING")
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            str: Base64 encoded encryption key
        """
        key = Fernet.generate_key()
        return key.decode()  # Fernet.generate_key() already returns base64 encoded bytes
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple[str, bytes]:
        """
        Derive encryption key from password
        
        Args:
            password: Password to derive key from
            salt: Salt for key derivation (generated if None)
            
        Returns:
            tuple: (base64_encoded_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt
    
    def encrypt_data(self, data: Union[Dict, list, str, bytes]) -> bytes:
        """
        Encrypt data
        
        Args:
            data: Data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        if not self.cipher_suite:
            SecurityLogger.log_security_event("encryption_skipped", "No encryption configured - storing data in plaintext", "WARNING")
            # Return serialized but unencrypted data
            if isinstance(data, (dict, list)):
                return json.dumps(data).encode()
            elif isinstance(data, str):
                return data.encode()
            else:
                return data
        
        try:
            # Serialize data if needed
            if isinstance(data, (dict, list)):
                data_bytes = json.dumps(data).encode()
            elif isinstance(data, str):
                data_bytes = data.encode()
            else:
                data_bytes = data
                
            encrypted_data = self.cipher_suite.encrypt(data_bytes)
            SecurityLogger.log_security_event("data_encrypted", f"Encrypted {len(data_bytes)} bytes")
            return encrypted_data
            
        except Exception as e:
            SecurityLogger.log_security_event("encryption_failed", f"Failed to encrypt data: {e}", "ERROR")
            raise
    
    def decrypt_data(self, encrypted_data: bytes, data_type: str = "json") -> Union[Dict, list, str]:
        """
        Decrypt data
        
        Args:
            encrypted_data: Encrypted data bytes
            data_type: Expected data type ("json", "str", "bytes")
            
        Returns:
            Decrypted data
        """
        if not self.cipher_suite:
            # Data was stored unencrypted
            try:
                if data_type == "json":
                    return json.loads(encrypted_data.decode())
                elif data_type == "str":
                    return encrypted_data.decode()
                else:
                    return encrypted_data
            except Exception as e:
                SecurityLogger.log_security_event("decryption_failed", f"Failed to decode unencrypted data: {e}", "ERROR")
                raise
        
        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_data)
            SecurityLogger.log_security_event("data_decrypted", f"Decrypted {len(decrypted_bytes)} bytes")
            
            if data_type == "json":
                return json.loads(decrypted_bytes.decode())
            elif data_type == "str":
                return decrypted_bytes.decode()
            else:
                return decrypted_bytes
                
        except Exception as e:
            SecurityLogger.log_security_event("decryption_failed", f"Failed to decrypt data: {e}", "ERROR")
            raise
    
    def save_secure_json(self, data: Union[Dict, list], file_path: Union[str, Path], backup: bool = True) -> None:
        """
        Save data as encrypted JSON file
        
        Args:
            data: Data to save
            file_path: Path to save file
            backup: Whether to create backup of existing file
        """
        file_path = Path(file_path)
        
        # Create backup if file exists
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            backup_path.write_bytes(file_path.read_bytes())
            SecurityLogger.log_security_event("backup_created", f"Backup created: {backup_path}")
        
        try:
            encrypted_data = self.encrypt_data(data)
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write encrypted data
            file_path.write_bytes(encrypted_data)
            
            # Set secure file permissions (600 - owner read/write only)
            file_path.chmod(0o600)
            
            SecurityLogger.log_data_access(str(file_path), "write", len(data) if isinstance(data, list) else 1)
            
        except Exception as e:
            SecurityLogger.log_security_event("secure_save_failed", f"Failed to save {file_path}: {e}", "ERROR")
            raise
    
    def load_secure_json(self, file_path: Union[str, Path]) -> Union[Dict, list]:
        """
        Load data from encrypted JSON file
        
        Args:
            file_path: Path to load file from
            
        Returns:
            Decrypted data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            encrypted_data = file_path.read_bytes()
            data = self.decrypt_data(encrypted_data, "json")
            
            SecurityLogger.log_data_access(str(file_path), "read", len(data) if isinstance(data, list) else 1)
            return data
            
        except Exception as e:
            SecurityLogger.log_security_event("secure_load_failed", f"Failed to load {file_path}: {e}", "ERROR")
            raise
    
    def secure_delete(self, file_path: Union[str, Path]) -> None:
        """
        Securely delete a file by overwriting it first
        
        Args:
            file_path: Path to file to delete
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return
        
        try:
            # Get file size
            file_size = file_path.stat().st_size
            
            # Overwrite with random data
            with open(file_path, 'r+b') as f:
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
            
            # Delete the file
            file_path.unlink()
            
            SecurityLogger.log_security_event("secure_delete", f"Securely deleted: {file_path}")
            
        except Exception as e:
            SecurityLogger.log_security_event("secure_delete_failed", f"Failed to securely delete {file_path}: {e}", "ERROR")
            raise
    
    def verify_file_integrity(self, file_path: Union[str, Path], expected_hash: str = None) -> str:
        """
        Verify file integrity using SHA-256 hash
        
        Args:
            file_path: Path to file to verify
            expected_hash: Expected hash to compare against
            
        Returns:
            str: SHA-256 hash of file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Calculate hash
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        file_hash = sha256_hash.hexdigest()
        
        if expected_hash and file_hash != expected_hash:
            SecurityLogger.log_security_event("integrity_check_failed", 
                                             f"File integrity check failed for {file_path}: expected {expected_hash}, got {file_hash}", 
                                             "ERROR")
            raise ValueError(f"File integrity check failed for {file_path}")
        
        SecurityLogger.log_security_event("integrity_check_passed", f"File integrity verified: {file_path}")
        return file_hash


def setup_encryption_key() -> str:
    """
    Setup encryption key for the application
    Generates new key if none exists in environment
    
    Returns:
        str: Base64 encoded encryption key
    """
    existing_key = os.getenv('DATA_ENCRYPTION_KEY')
    
    if existing_key:
        print("✅ Encryption key found in environment")
        return existing_key
    
    print("⚠️  No encryption key found. Generating new key...")
    new_key = SecureStorage.generate_key()
    
    print(f"""
🔑 Generated new encryption key: {new_key}

IMPORTANT: Add this to your .env file:
DATA_ENCRYPTION_KEY={new_key}

Keep this key secure! If you lose it, encrypted data cannot be recovered.
""")
    
    return new_key


if __name__ == "__main__":
    # Test the secure storage functionality
    print("Testing SecureStorage...")
    
    # Setup encryption
    key = setup_encryption_key()
    storage = SecureStorage(key)
    
    # Test data
    test_data = {
        "licenses": [
            {"id": "12345", "date": "2025-09-05", "type": "restaurant"},
            {"id": "67890", "date": "2025-09-04", "type": "retail"}
        ],
        "metadata": {"last_updated": "2025-09-05T10:00:00Z"}
    }
    
    # Test encryption/decryption
    print("Testing encryption...")
    test_file = Path("test_secure_data.enc")
    
    try:
        storage.save_secure_json(test_data, test_file)
        print(f"✅ Data saved securely to {test_file}")
        
        loaded_data = storage.load_secure_json(test_file)
        print(f"✅ Data loaded successfully: {len(loaded_data['licenses'])} records")
        
        # Verify integrity
        file_hash = storage.verify_file_integrity(test_file)
        print(f"✅ File integrity verified: {file_hash[:16]}...")
        
        # Clean up
        storage.secure_delete(test_file)
        print("✅ Test file securely deleted")
        
        print("\n🔒 Secure storage test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if test_file.exists():
            test_file.unlink()  # Clean up on failure