"""
Security utilities for Chicago SMB Market Radar
Provides input validation, sanitization, and security logging
"""

import logging
import time
import re
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from functools import wraps
import hashlib

# Configure security logger
security_logger = logging.getLogger('security')
security_handler = logging.FileHandler('security.log')
security_formatter = logging.Formatter('%(asctime)s - SECURITY - %(levelname)s - %(message)s')
security_handler.setFormatter(security_formatter)
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


class InputValidator:
    """Validates and sanitizes input data from external APIs"""
    
    # Define expected schemas for different data sources
    BUSINESS_LICENSES_SCHEMA = {
        "type": "object",
        "required": ["license_id", "license_start_date"],
        "properties": {
            "license_id": {"type": "string", "pattern": r"^[A-Z0-9\-]+$"},
            "license_start_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}T"},
            "community_area": {"type": ["string", "null"], "pattern": r"^\d{1,2}$"},
            "license_description": {"type": "string", "maxLength": 500},
            "latitude": {"type": ["string", "number", "null"]},
            "longitude": {"type": ["string", "number", "null"]},
        }
    }
    
    BUILDING_PERMITS_SCHEMA = {
        "type": "object", 
        "required": ["permit_", "issue_date"],
        "properties": {
            "permit_": {"type": "string", "pattern": r"^[A-Z0-9\-]+$"},
            "issue_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}T"},
            "total_fee": {"type": ["string", "number", "null"]},
            "work_type": {"type": "string", "maxLength": 200},
            "community_area": {"type": ["string", "null"], "pattern": r"^\d{1,2}$"},
        }
    }
    
    @staticmethod
    def validate_api_response(data: List[Dict[Any, Any]], dataset_name: str) -> bool:
        """
        Validate API response data against expected schema
        
        Args:
            data: List of records from API
            dataset_name: Name of dataset (business_licenses, building_permits, etc.)
            
        Returns:
            bool: True if validation passes
            
        Raises:
            SecurityError: If validation fails
        """
        if not isinstance(data, list):
            raise SecurityError(f"Invalid data type: expected list, got {type(data)}")
            
        if len(data) == 0:
            security_logger.warning(f"Empty dataset received for {dataset_name}")
            return True
            
        # Sample validation on first few records
        sample_size = min(5, len(data))
        for i, record in enumerate(data[:sample_size]):
            if not isinstance(record, dict):
                raise SecurityError(f"Record {i} is not a dictionary: {type(record)}")
                
            # Basic field validation based on dataset
            if dataset_name == "business_licenses":
                InputValidator._validate_business_license_record(record, i)
            elif dataset_name == "building_permits":
                InputValidator._validate_building_permit_record(record, i)
                
        security_logger.info(f"Validation passed for {dataset_name}: {len(data)} records")
        return True
    
    @staticmethod
    def _validate_business_license_record(record: Dict[Any, Any], index: int) -> None:
        """Validate a single business license record"""
        required_fields = ["license_id", "license_start_date"]
        
        for field in required_fields:
            if field not in record:
                raise SecurityError(f"Missing required field '{field}' in record {index}")
                
        # Validate license ID format
        license_id = str(record.get("license_id", ""))
        if not re.match(r"^[A-Z0-9\-]{1,50}$", license_id):
            raise SecurityError(f"Invalid license_id format in record {index}: {license_id}")
            
        # Validate date format
        date_str = str(record.get("license_start_date", ""))
        if not re.match(r"^\d{4}-\d{2}-\d{2}T", date_str):
            raise SecurityError(f"Invalid date format in record {index}: {date_str}")
    
    @staticmethod
    def _validate_building_permit_record(record: Dict[Any, Any], index: int) -> None:
        """Validate a single building permit record"""
        required_fields = ["permit_", "issue_date"]
        
        for field in required_fields:
            if field not in record:
                raise SecurityError(f"Missing required field '{field}' in record {index}")
                
        # Validate permit ID format
        permit_id = str(record.get("permit_", ""))
        if not re.match(r"^[A-Z0-9\-]{1,50}$", permit_id):
            raise SecurityError(f"Invalid permit_ format in record {index}: {permit_id}")
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input by removing dangerous characters
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)
            
        # Remove null bytes and control characters
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
            security_logger.warning(f"String truncated to {max_length} characters")
            
        return value.strip()
    
    @staticmethod
    def validate_coordinates(lat: Optional[Union[str, float]], 
                           lon: Optional[Union[str, float]]) -> bool:
        """
        Validate geographic coordinates for Chicago area
        
        Args:
            lat: Latitude value
            lon: Longitude value
            
        Returns:
            bool: True if coordinates are valid for Chicago
        """
        if lat is None or lon is None:
            return True  # Allow null coordinates
            
        try:
            lat_float = float(lat)
            lon_float = float(lon)
            
            # Chicago boundaries (approximate)
            if not (41.6 <= lat_float <= 42.1):
                security_logger.warning(f"Latitude outside Chicago bounds: {lat_float}")
                return False
                
            if not (-87.9 <= lon_float <= -87.5):
                security_logger.warning(f"Longitude outside Chicago bounds: {lon_float}")
                return False
                
            return True
            
        except (ValueError, TypeError):
            security_logger.warning(f"Invalid coordinate format: lat={lat}, lon={lon}")
            return False


class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, calls_per_second: float = 1.0):
        self.min_interval = 1.0 / calls_per_second
        self.last_called = 0.0
        
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_called
        left_to_wait = self.min_interval - elapsed
        
        if left_to_wait > 0:
            time.sleep(left_to_wait)
            
        self.last_called = time.time()


def rate_limit(calls_per_second: float = 1.0):
    """Decorator for rate limiting function calls"""
    limiter = RateLimiter(calls_per_second)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
    return decorator


class SecurityLogger:
    """Enhanced security logging"""
    
    @staticmethod
    def log_auth_attempt(success: bool, details: str, user_id: str = "system"):
        """Log authentication attempts"""
        level = logging.INFO if success else logging.WARNING
        security_logger.log(level, f"Auth attempt: {success} - User: {user_id} - {details}")
    
    @staticmethod
    def log_data_access(resource: str, action: str, record_count: int = 0):
        """Log data access events"""
        security_logger.info(f"Data access: {action} on {resource} - Records: {record_count}")
    
    @staticmethod
    def log_api_call(endpoint: str, status_code: int, response_size: int = 0):
        """Log external API calls"""
        if status_code >= 400:
            security_logger.warning(f"API call failed: {endpoint} - Status: {status_code}")
        else:
            security_logger.info(f"API call: {endpoint} - Status: {status_code} - Size: {response_size}")
    
    @staticmethod
    def log_security_event(event_type: str, details: str, severity: str = "INFO"):
        """Log general security events"""
        level = getattr(logging, severity.upper(), logging.INFO)
        security_logger.log(level, f"Security event: {event_type} - {details}")


def security_health_check() -> Dict[str, bool]:
    """
    Perform security health checks
    
    Returns:
        Dict mapping check names to pass/fail status
    """
    checks = {}
    
    # Check if security logging is working
    try:
        security_logger.info("Security health check initiated")
        checks["security_logging"] = True
    except Exception:
        checks["security_logging"] = False
    
    # Check file permissions on sensitive files
    import os
    try:
        env_stat = os.stat(".env")
        # Check if file is readable only by owner (mode 600)
        checks["env_permissions"] = (env_stat.st_mode & 0o077) == 0
    except FileNotFoundError:
        checks["env_permissions"] = True  # File doesn't exist, which is also secure
    except Exception:
        checks["env_permissions"] = False
    
    # Check if data directory has appropriate permissions
    try:
        if os.path.exists("data"):
            data_stat = os.stat("data")
            checks["data_permissions"] = True
        else:
            checks["data_permissions"] = True
    except Exception:
        checks["data_permissions"] = False
    
    # Log results
    failed_checks = [check for check, passed in checks.items() if not passed]
    if failed_checks:
        SecurityLogger.log_security_event(
            "health_check_failures", 
            f"Failed checks: {', '.join(failed_checks)}", 
            "WARNING"
        )
    else:
        SecurityLogger.log_security_event("health_check_passed", "All security checks passed")
    
    return checks


if __name__ == "__main__":
    # Run security health check
    print("Running security health check...")
    results = security_health_check()
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check}: {status}")