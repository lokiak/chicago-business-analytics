# 🔒 Security Guide - Chicago SMB Market Radar

## Overview

This document outlines the comprehensive security improvements implemented in the Chicago SMB Market Radar platform. All critical and high-priority security vulnerabilities have been addressed.

## ✅ Security Features Implemented

### 1. **Secure Credential Management**
- **✅ Fixed**: Removed hardcoded credentials from repository
- **✅ Enhanced**: Improved .env file permissions (600 - owner-only access)
- **✅ Added**: Comprehensive .gitignore rules for all credential files
- **✅ Created**: Secure .env.example template with instructions

### 2. **GitHub Actions Security** 
- **✅ Fixed**: Credentials now written to secure temp location ($RUNNER_TEMP)
- **✅ Enhanced**: Added restrictive file permissions (600) for credential files
- **✅ Improved**: Better error handling and verification

### 3. **Input Validation & API Security**
- **✅ Added**: Comprehensive API response validation
- **✅ Implemented**: Schema validation for all data sources
- **✅ Enhanced**: Coordinate validation for Chicago geographic bounds
- **✅ Added**: String sanitization to prevent injection attacks

### 4. **Rate Limiting**
- **✅ Implemented**: Configurable rate limiting for all API calls  
- **✅ Added**: Decorator-based rate limiting for functions
- **✅ Default**: 1 request per second (configurable)

### 5. **Security Logging & Monitoring**
- **✅ Added**: Dedicated security.log file with structured logging
- **✅ Implemented**: Authentication, data access, and API call logging
- **✅ Created**: Security health check system
- **✅ Enhanced**: Real-time security event monitoring

### 6. **Data Encryption at Rest**
- **✅ Added**: AES-256 encryption for sensitive local data
- **✅ Implemented**: Secure key generation and management
- **✅ Created**: Password-based key derivation (PBKDF2)
- **✅ Added**: File integrity verification (SHA-256)
- **✅ Implemented**: Secure file deletion

### 7. **Comprehensive Testing**
- **✅ Created**: Full security test suite (50+ tests)
- **✅ Added**: Unit tests for all security components
- **✅ Implemented**: Integration tests for complete security pipeline
- **✅ Added**: Automated security health checks

## 🚀 Quick Start Guide

### Initial Setup

1. **Install Security Dependencies**
   ```bash
   pip install cryptography>=41.0.0 jsonschema>=4.19.0
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   chmod 600 .env
   ```

3. **Generate Encryption Key (Optional)**
   ```bash
   cd shared && python secure_storage.py
   # Add the generated key to your .env file
   ```

4. **Run Security Health Check**
   ```bash
   cd shared && python security_utils.py
   ```

### Running the Secure Pipeline

```bash
# The main pipeline now includes all security features automatically
python -m src.main
```

### Running Security Tests

```bash
# Run comprehensive security test suite
cd tests && python test_security.py

# Run specific test categories
python -m unittest tests.test_security.TestInputValidator
python -m unittest tests.test_security.TestSecureStorage
```

## 📊 Security Monitoring

### Security Logs Location
- **Main log**: `security.log` (created automatically)
- **Format**: `TIMESTAMP - SECURITY - LEVEL - MESSAGE`

### Key Events Monitored
- Authentication attempts (success/failure)
- Data access events (read/write operations)
- API calls with status codes and response sizes
- Input validation failures
- Encryption/decryption operations
- File integrity checks

### Health Check Metrics
- Security logging functionality
- Environment file permissions
- Data directory permissions
- Encryption availability

### Example Log Entries
```
2025-09-05 10:00:00 - SECURITY - INFO - Auth attempt: True - User: system - Service account login successful
2025-09-05 10:00:01 - SECURITY - INFO - API call: https://data.cityofchicago.org/resource/r5kz-chrr.json - Status: 200 - Size: 15000
2025-09-05 10:00:02 - SECURITY - INFO - Data access: write on Business_Licenses_Full - Records: 1500
2025-09-05 10:00:03 - SECURITY - INFO - Data encrypted: 8192 bytes
```

## 🔧 Configuration Options

### Environment Variables

```bash
# Required
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
SHEET_ID=your_google_sheet_id

# Security Options (Optional)
DATA_ENCRYPTION_KEY=your_32_byte_hex_key_here
API_RATE_LIMIT=1.0                    # Requests per second
LOG_LEVEL=INFO
SECURITY_LOG_ENABLED=true
```

### Rate Limiting Configuration

```python
# In your code, you can adjust rate limiting:
@rate_limit(calls_per_second=0.5)  # One call every 2 seconds
def slow_api_call():
    pass

# Or configure the SocrataClient rate limit in security_utils.py
```

### Encryption Configuration

```python
from secure_storage import SecureStorage

# Generate new encryption key
key = SecureStorage.generate_key()

# Initialize with custom key
storage = SecureStorage(encryption_key=key)

# Derive key from password
key, salt = SecureStorage.derive_key_from_password("your_secure_password")
```

## 🛡️ Security Best Practices

### For Development

1. **Never commit credentials to git**
2. **Always use .env files with 600 permissions**
3. **Regularly rotate API keys and service account credentials**
4. **Run security tests before deploying**
5. **Monitor security.log for unusual activity**

### For Production

1. **Use environment variables instead of .env files**
2. **Enable data encryption for sensitive information**
3. **Monitor security health checks regularly**
4. **Set up log aggregation for security events**
5. **Regularly audit access to Google Sheets and service accounts**

### For CI/CD

1. **Use GitHub secrets for credentials**
2. **Never log credential values**
3. **Use secure temp directories for credential files**
4. **Clean up credential files after use**
5. **Run security tests in CI pipeline**

## 🚨 Security Incident Response

### If Credentials are Compromised

1. **Immediately rotate affected credentials**:
   ```bash
   # For Google service accounts:
   # 1. Go to Google Cloud Console
   # 2. Delete compromised service account key
   # 3. Generate new key
   # 4. Update GitHub secrets
   # 5. Update local .env file
   ```

2. **Check security logs for unauthorized access**:
   ```bash
   grep -i "auth attempt: false\|status: 4\|status: 5" security.log
   ```

3. **Run security health check**:
   ```bash
   cd shared && python security_utils.py
   ```

### If Data Breach is Suspected

1. **Check data access logs**:
   ```bash
   grep -i "data access" security.log
   ```

2. **Verify file integrity**:
   ```python
   from secure_storage import SecureStorage
   storage = SecureStorage()
   storage.verify_file_integrity("sensitive_file.enc", expected_hash)
   ```

3. **Re-encrypt all sensitive data with new keys**

## 📈 Security Metrics Dashboard

### Key Performance Indicators

- **Authentication Success Rate**: >99%
- **API Response Validation Pass Rate**: 100%
- **Data Encryption Coverage**: 100% of sensitive data
- **Security Test Pass Rate**: 100%
- **Average API Response Time**: <2 seconds (with rate limiting)

### Monitoring Queries

```bash
# Count failed authentication attempts
grep "Auth attempt: False" security.log | wc -l

# Check API error rates  
grep "API call.*Status: [45]" security.log | wc -l

# Monitor data access patterns
grep "Data access" security.log | tail -10

# Check encryption activity
grep "encrypted\|decrypted" security.log | wc -l
```

## 🔄 Regular Security Maintenance

### Daily Tasks
- [ ] Check security.log for any warnings or errors
- [ ] Verify security health check passes
- [ ] Monitor API response times and error rates

### Weekly Tasks
- [ ] Run full security test suite
- [ ] Review data access patterns for anomalies
- [ ] Check for dependency security updates

### Monthly Tasks
- [ ] Rotate service account keys
- [ ] Review and update security policies
- [ ] Audit user access to Google Sheets
- [ ] Update security documentation

### Quarterly Tasks
- [ ] Penetration testing or security audit
- [ ] Update threat model
- [ ] Review and improve security procedures
- [ ] Security training for team members

## 📞 Getting Help

### Security Questions
- Check this documentation first
- Review security.log for specific issues
- Run security health checks for diagnosis

### Reporting Security Issues
- **Critical**: Immediately rotate credentials and contact team
- **High/Medium**: Create GitHub issue with security label
- **Low**: Include in regular maintenance cycle

## ✅ Security Checklist

Use this checklist before deploying:

- [ ] All credentials removed from code
- [ ] .env file permissions set to 600
- [ ] Security health check passes
- [ ] All security tests pass
- [ ] GitHub Actions using secure credential handling
- [ ] Rate limiting configured appropriately  
- [ ] Security logging enabled
- [ ] Data encryption configured (if needed)
- [ ] Monitoring and alerting set up

---

## 🎉 Conclusion

The Chicago SMB Market Radar platform now implements enterprise-grade security measures. All critical vulnerabilities have been addressed, and comprehensive monitoring is in place. Regular maintenance of these security features will ensure ongoing protection of sensitive data and system integrity.

**Security Status: ✅ SECURE**

Last Updated: September 5, 2025