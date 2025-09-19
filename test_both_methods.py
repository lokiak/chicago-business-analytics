#!/usr/bin/env python3
"""
Test both credential encoding methods
"""

import json
import base64
import tempfile
import os

def test_json_string_method():
    """Test using raw JSON string"""
    print("🧪 Testing JSON String Method")
    print("-" * 40)

    # Read the JSON file
    with open('/Users/loki/api_keys/google_cloud/ravenswood-consulting-c3a2e60d67a9.json', 'r') as f:
        json_content = f.read()

    print(f"✅ JSON content length: {len(json_content)} characters")

    # Verify it's valid JSON
    try:
        parsed = json.loads(json_content)
        print(f"✅ Valid JSON with {len(parsed)} keys")
        print(f"✅ Service account: {parsed.get('client_email', 'unknown')}")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False

    # Test writing to temp file (like GitHub Actions would)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(json_content)
        temp_path = f.name

    # Test reading it back
    try:
        with open(temp_path, 'r') as f:
            reloaded = json.load(f)
        print(f"✅ Successfully wrote and reloaded from temp file")
        os.unlink(temp_path)
        return True
    except Exception as e:
        print(f"❌ Failed to reload: {e}")
        os.unlink(temp_path)
        return False

def test_base64_method():
    """Test using base64 encoding"""
    print("\n🧪 Testing Base64 Method")
    print("-" * 40)

    # Read and encode the file
    with open('/Users/loki/api_keys/google_cloud/ravenswood-consulting-c3a2e60d67a9.json', 'rb') as f:
        file_bytes = f.read()

    # Encode to base64
    b64_encoded = base64.b64encode(file_bytes).decode('utf-8')
    print(f"✅ Base64 encoded length: {len(b64_encoded)} characters")

    # Test decoding
    try:
        decoded_bytes = base64.b64decode(b64_encoded)
        decoded_json = decoded_bytes.decode('utf-8')
        parsed = json.loads(decoded_json)
        print(f"✅ Successfully decoded and parsed JSON")
        print(f"✅ Service account: {parsed.get('client_email', 'unknown')}")

        # Test writing to temp file (like GitHub Actions would)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(decoded_json)
            temp_path = f.name

        with open(temp_path, 'r') as f:
            reloaded = json.load(f)
        print(f"✅ Successfully wrote and reloaded from temp file")
        os.unlink(temp_path)
        return True, b64_encoded

    except Exception as e:
        print(f"❌ Base64 decode failed: {e}")
        return False, None

def main():
    """Test both methods"""
    print("🔐 Testing Credential Encoding Methods")
    print("=" * 50)

    # Test JSON string method
    json_success = test_json_string_method()

    # Test base64 method
    base64_success, b64_string = test_base64_method()

    print("\n" + "=" * 50)
    print("📋 RESULTS SUMMARY")
    print("=" * 50)

    if json_success:
        print("✅ JSON String Method: WORKS")
        print("   - Simpler to implement")
        print("   - Easier to debug")
        print("   - Need to be careful with quotes/newlines")
    else:
        print("❌ JSON String Method: FAILED")

    if base64_success:
        print("✅ Base64 Method: WORKS")
        print("   - More robust for special characters")
        print("   - Industry standard")
        print("   - Slightly more complex")
    else:
        print("❌ Base64 Method: FAILED")

    print("\n📋 RECOMMENDATIONS:")
    if base64_success:
        print("🏆 Use Base64 method (more reliable)")
        print(f"   GitHub Secret Value: {b64_string[:50]}...")
    elif json_success:
        print("🥈 Use JSON String method (simpler)")
        print("   Copy the raw JSON content to GitHub secret")
    else:
        print("❌ Both methods failed - need to investigate")

if __name__ == "__main__":
    main()
