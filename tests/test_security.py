"""
Comprehensive security tests for Chicago SMB Market Radar
Tests all security features including validation, encryption, logging, and rate limiting
"""

import unittest
import tempfile
import os
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from security_utils import (
    InputValidator, SecurityError, RateLimiter, rate_limit,
    SecurityLogger, security_health_check
)
from secure_storage import SecureStorage


class TestInputValidator(unittest.TestCase):
    """Test input validation functionality"""
    
    def setUp(self):
        self.validator = InputValidator()
    
    def test_valid_business_license_data(self):
        """Test validation of valid business license data"""
        valid_data = [
            {
                "license_id": "ABCD-12345",
                "license_start_date": "2025-09-01T00:00:00.000",
                "community_area": "12",
                "license_description": "Restaurant License",
                "latitude": "41.8781",
                "longitude": "-87.6298"
            }
        ]
        
        # Should not raise exception
        result = self.validator.validate_api_response(valid_data, "business_licenses")
        self.assertTrue(result)
    
    def test_invalid_business_license_missing_required_field(self):
        """Test validation fails for missing required fields"""
        invalid_data = [
            {
                "license_start_date": "2025-09-01T00:00:00.000",
                # Missing license_id
                "community_area": "12"
            }
        ]
        
        with self.assertRaises(SecurityError) as context:
            self.validator.validate_api_response(invalid_data, "business_licenses")
        
        self.assertIn("Missing required field 'license_id'", str(context.exception))
    
    def test_invalid_license_id_format(self):
        """Test validation fails for invalid license ID format"""
        invalid_data = [
            {
                "license_id": "invalid<script>alert('xss')</script>",
                "license_start_date": "2025-09-01T00:00:00.000"
            }
        ]
        
        with self.assertRaises(SecurityError) as context:
            self.validator.validate_api_response(invalid_data, "business_licenses")
        
        self.assertIn("Invalid license_id format", str(context.exception))
    
    def test_invalid_date_format(self):
        """Test validation fails for invalid date format"""
        invalid_data = [
            {
                "license_id": "ABCD-12345",
                "license_start_date": "invalid-date-format"
            }
        ]
        
        with self.assertRaises(SecurityError) as context:
            self.validator.validate_api_response(invalid_data, "business_licenses")
        
        self.assertIn("Invalid date format", str(context.exception))
    
    def test_valid_building_permit_data(self):
        """Test validation of valid building permit data"""
        valid_data = [
            {
                "permit_": "PERMIT-67890",
                "issue_date": "2025-09-01T00:00:00.000",
                "total_fee": "150.00",
                "work_type": "Electrical",
                "community_area": "8"
            }
        ]
        
        result = self.validator.validate_api_response(valid_data, "building_permits")
        self.assertTrue(result)
    
    def test_empty_dataset(self):
        """Test validation passes for empty dataset"""
        empty_data = []
        result = self.validator.validate_api_response(empty_data, "business_licenses")
        self.assertTrue(result)
    
    def test_coordinate_validation_chicago_bounds(self):
        """Test coordinate validation for Chicago area"""
        # Valid Chicago coordinates
        self.assertTrue(self.validator.validate_coordinates(41.8781, -87.6298))
        
        # Invalid coordinates (outside Chicago)
        self.assertFalse(self.validator.validate_coordinates(40.0, -87.6298))  # Too far south
        self.assertFalse(self.validator.validate_coordinates(41.8781, -90.0))  # Too far west
        
        # Null coordinates should be allowed
        self.assertTrue(self.validator.validate_coordinates(None, None))
        
        # Invalid format
        self.assertFalse(self.validator.validate_coordinates("invalid", "coordinates"))
    
    def test_string_sanitization(self):
        """Test string sanitization functionality"""
        dangerous_string = "Test\x00String\x0BWith\x1FControl\x7FChars"
        sanitized = self.validator.sanitize_string(dangerous_string)
        self.assertEqual(sanitized, "TestStringWithControlChars")
        
        # Test length limiting
        long_string = "A" * 2000
        sanitized_long = self.validator.sanitize_string(long_string, max_length=100)
        self.assertEqual(len(sanitized_long), 100)


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def test_rate_limiter_basic(self):
        """Test basic rate limiting functionality"""
        limiter = RateLimiter(calls_per_second=2.0)  # 2 calls per second = 0.5s interval
        
        start_time = time.time()
        
        # First call should be immediate
        limiter.wait_if_needed()
        first_call_time = time.time()
        
        # Second call should wait
        limiter.wait_if_needed()
        second_call_time = time.time()
        
        # Should have waited approximately 0.5 seconds
        elapsed = second_call_time - first_call_time
        self.assertGreaterEqual(elapsed, 0.4)  # Allow some tolerance
        self.assertLessEqual(elapsed, 0.6)
    
    def test_rate_limit_decorator(self):
        """Test rate limiting decorator"""
        call_times = []
        
        @rate_limit(calls_per_second=3.0)  # 3 calls per second = ~0.33s interval
        def test_function():
            call_times.append(time.time())
            return "called"
        
        # Make multiple calls
        for _ in range(3):
            result = test_function()
            self.assertEqual(result, "called")
        
        # Check timing intervals
        self.assertEqual(len(call_times), 3)
        
        # Second call should be delayed
        if len(call_times) >= 2:
            interval = call_times[1] - call_times[0]
            self.assertGreaterEqual(interval, 0.3)


class TestSecureStorage(unittest.TestCase):
    """Test secure storage functionality"""
    
    def setUp(self):
        # Generate a test key
        self.test_key = SecureStorage.generate_key()
        self.storage = SecureStorage(self.test_key)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temp files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_key_generation(self):
        """Test encryption key generation"""
        key1 = SecureStorage.generate_key()
        key2 = SecureStorage.generate_key()
        
        # Keys should be different
        self.assertNotEqual(key1, key2)
        
        # Keys should be valid base64
        import base64
        try:
            base64.urlsafe_b64decode(key1.encode())
            base64.urlsafe_b64decode(key2.encode())
        except Exception:
            self.fail("Generated keys are not valid base64")
    
    def test_password_key_derivation(self):
        """Test key derivation from password"""
        password = "test_password_123"
        key1, salt1 = SecureStorage.derive_key_from_password(password)
        key2, salt2 = SecureStorage.derive_key_from_password(password, salt1)
        
        # Same password + salt should produce same key
        self.assertEqual(key1, key2)
        
        # Different salt should produce different key
        key3, salt3 = SecureStorage.derive_key_from_password(password)
        self.assertNotEqual(key1, key3)
    
    def test_data_encryption_decryption(self):
        """Test data encryption and decryption"""
        test_data = {
            "licenses": [
                {"id": "12345", "type": "restaurant", "date": "2025-09-05"},
                {"id": "67890", "type": "retail", "date": "2025-09-04"}
            ],
            "metadata": {"count": 2, "last_updated": "2025-09-05T10:00:00Z"}
        }
        
        # Encrypt data
        encrypted = self.storage.encrypt_data(test_data)
        self.assertIsInstance(encrypted, bytes)
        self.assertNotEqual(encrypted, json.dumps(test_data).encode())
        
        # Decrypt data
        decrypted = self.storage.decrypt_data(encrypted, "json")
        self.assertEqual(decrypted, test_data)
    
    def test_secure_file_operations(self):
        """Test secure file save and load operations"""
        test_data = [
            {"id": "TEST-001", "value": "sensitive_data_1"},
            {"id": "TEST-002", "value": "sensitive_data_2"}
        ]
        
        test_file = Path(self.temp_dir) / "test_secure.enc"
        
        # Save data securely
        self.storage.save_secure_json(test_data, test_file)
        
        # File should exist and have correct permissions
        self.assertTrue(test_file.exists())
        stat_info = test_file.stat()
        # Check if file is readable only by owner (600 permissions)
        self.assertEqual(stat_info.st_mode & 0o777, 0o600)
        
        # Load data securely
        loaded_data = self.storage.load_secure_json(test_file)
        self.assertEqual(loaded_data, test_data)
    
    def test_file_integrity_verification(self):
        """Test file integrity verification"""
        test_file = Path(self.temp_dir) / "integrity_test.txt"
        test_content = "This is test content for integrity check"
        
        # Write test file
        test_file.write_text(test_content)
        
        # Get hash
        file_hash = self.storage.verify_file_integrity(test_file)
        self.assertIsInstance(file_hash, str)
        self.assertEqual(len(file_hash), 64)  # SHA-256 hash length
        
        # Verify with expected hash
        verified_hash = self.storage.verify_file_integrity(test_file, file_hash)
        self.assertEqual(verified_hash, file_hash)
        
        # Test integrity failure
        with self.assertRaises(ValueError):
            self.storage.verify_file_integrity(test_file, "wrong_hash")
    
    def test_secure_delete(self):
        """Test secure file deletion"""
        test_file = Path(self.temp_dir) / "delete_test.txt"
        test_content = "sensitive content to delete"
        
        # Create test file
        test_file.write_text(test_content)
        self.assertTrue(test_file.exists())
        
        # Securely delete
        self.storage.secure_delete(test_file)
        
        # File should be gone
        self.assertFalse(test_file.exists())
    
    def test_storage_without_encryption(self):
        """Test storage operations when no encryption key is provided"""
        unencrypted_storage = SecureStorage(encryption_key=None)
        test_data = {"test": "data"}
        
        # Should still work but store unencrypted
        encrypted = unencrypted_storage.encrypt_data(test_data)
        decrypted = unencrypted_storage.decrypt_data(encrypted, "json")
        
        self.assertEqual(decrypted, test_data)


class TestSecurityLogger(unittest.TestCase):
    """Test security logging functionality"""
    
    def test_auth_logging(self):
        """Test authentication logging"""
        with patch('security_utils.security_logger') as mock_logger:
            SecurityLogger.log_auth_attempt(True, "Service account login", "system")
            SecurityLogger.log_auth_attempt(False, "Invalid credentials", "unknown")
            
            # Verify logging was called
            self.assertEqual(mock_logger.log.call_count, 2)
    
    def test_data_access_logging(self):
        """Test data access logging"""
        with patch('security_utils.security_logger') as mock_logger:
            SecurityLogger.log_data_access("business_licenses", "read", 1000)
            SecurityLogger.log_api_call("https://api.example.com/data", 200, 5000)
            
            # Verify logging was called
            self.assertTrue(mock_logger.info.called)
    
    def test_security_event_logging(self):
        """Test general security event logging"""
        with patch('security_utils.security_logger') as mock_logger:
            SecurityLogger.log_security_event("test_event", "Test details", "WARNING")
            
            # Verify logging was called with correct level
            mock_logger.log.assert_called()


class TestSecurityHealthCheck(unittest.TestCase):
    """Test security health check functionality"""
    
    def test_health_check_execution(self):
        """Test that health check runs without errors"""
        results = security_health_check()
        
        # Should return a dictionary of check results
        self.assertIsInstance(results, dict)
        
        # Should have at least basic checks
        expected_checks = ["security_logging", "env_permissions", "data_permissions"]
        for check in expected_checks:
            self.assertIn(check, results)
            self.assertIsInstance(results[check], bool)
    
    @patch.dict(os.environ, {'DATA_ENCRYPTION_KEY': 'test_key'})
    def test_health_check_with_environment(self):
        """Test health check with environment variables set"""
        results = security_health_check()
        
        # Should pass basic checks
        self.assertIn("security_logging", results)


class TestIntegrationSecurity(unittest.TestCase):
    """Integration tests for security components working together"""
    
    def setUp(self):
        self.test_key = SecureStorage.generate_key()
        self.storage = SecureStorage(self.test_key)
        self.validator = InputValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_secure_data_pipeline(self):
        """Test complete secure data processing pipeline"""
        # Simulate API response data
        raw_api_data = [
            {
                "license_id": "REST-12345",
                "license_start_date": "2025-09-01T00:00:00.000",
                "community_area": "12",
                "license_description": "Restaurant - Full Service",
                "latitude": "41.8781",
                "longitude": "-87.6298"
            },
            {
                "license_id": "RETAIL-67890", 
                "license_start_date": "2025-09-02T00:00:00.000",
                "community_area": "8",
                "license_description": "Retail Store",
                "latitude": "41.8500",
                "longitude": "-87.6000"
            }
        ]
        
        # Step 1: Validate incoming data
        validation_result = self.validator.validate_api_response(raw_api_data, "business_licenses")
        self.assertTrue(validation_result)
        
        # Step 2: Sanitize string fields
        for record in raw_api_data:
            record["license_description"] = self.validator.sanitize_string(record["license_description"])
        
        # Step 3: Validate coordinates
        for record in raw_api_data:
            lat = record.get("latitude")
            lon = record.get("longitude")
            if lat and lon:
                coords_valid = self.validator.validate_coordinates(lat, lon)
                self.assertTrue(coords_valid, f"Invalid coordinates: {lat}, {lon}")
        
        # Step 4: Securely store processed data
        secure_file = Path(self.temp_dir) / "processed_licenses.enc"
        self.storage.save_secure_json(raw_api_data, secure_file)
        
        # Step 5: Verify secure storage worked
        self.assertTrue(secure_file.exists())
        loaded_data = self.storage.load_secure_json(secure_file)
        self.assertEqual(len(loaded_data), 2)
        self.assertEqual(loaded_data[0]["license_id"], "REST-12345")
        
        # Step 6: Verify file integrity
        file_hash = self.storage.verify_file_integrity(secure_file)
        self.assertIsInstance(file_hash, str)
        
        # Step 7: Clean up securely
        self.storage.secure_delete(secure_file)
        self.assertFalse(secure_file.exists())


def run_security_tests():
    """Run all security tests"""
    print("🔒 Running comprehensive security tests...\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestInputValidator,
        TestRateLimiter,
        TestSecureStorage,
        TestSecurityLogger,
        TestSecurityHealthCheck,
        TestIntegrationSecurity
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    if result.wasSuccessful():
        print("🎉 ALL SECURITY TESTS PASSED!")
        print(f"✅ {result.testsRun} tests completed successfully")
    else:
        print("❌ SECURITY TESTS FAILED!")
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors out of {result.testsRun} tests")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
                
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the security test suite
    success = run_security_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)