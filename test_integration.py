#!/usr/bin/env python3
"""
Integration test script for TerminalChat
Tests the complete flow of server and client communication
"""

import subprocess
import time
import socket
import sys


def check_port_available(port):
    """Check if a port is available."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', port))
        sock.close()
        return True
    except OSError:
        return False


def test_server_startup():
    """Test that server starts and stops cleanly."""
    print("Testing server startup...")
    
    if not check_port_available(9999):
        print("✗ Port 9999 is already in use")
        return False
    
    server_process = subprocess.Popen(
        ['python', 'server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    
    # Check if server is running
    if server_process.poll() is not None:
        print("✗ Server failed to start")
        return False
    
    print("✓ Server started successfully")
    
    # Stop server
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
        print("✓ Server stopped cleanly")
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()
        print("✓ Server stopped (forced)")
    
    return True


def test_client_connection():
    """Test that client can connect to server."""
    print("\nTesting client connection...")
    
    # Start server
    server_process = subprocess.Popen(
        ['python', 'server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    
    # Try to connect with client
    client_process = subprocess.Popen(
        ['python', 'client.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    
    # Send quit command
    client_process.stdin.write('/quit\n')
    client_process.stdin.flush()
    
    try:
        client_process.wait(timeout=3)
        print("✓ Client connected and disconnected cleanly")
        success = True
    except subprocess.TimeoutExpired:
        print("✗ Client did not exit cleanly")
        client_process.kill()
        success = False
    
    # Stop server
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()
    
    return success


def test_encryption():
    """Test encryption module independently."""
    print("\nTesting encryption module...")
    
    result = subprocess.run(
        ['python', '-c', '''
from encryption import SecureEncryption

enc1 = SecureEncryption()
enc2 = SecureEncryption()

enc1.set_peer_public_key(enc2.get_public_key_bytes())
enc2.set_peer_public_key(enc1.get_public_key_bytes())

session_key = enc1.generate_session_key()
encrypted_key = enc1.encrypt_session_key()
decrypted_key = enc2.decrypt_session_key(encrypted_key)

assert session_key == decrypted_key

test_message = "Test message"
iv, ciphertext, tag = enc1.encrypt_message(test_message)
decrypted = enc2.decrypt_message(iv, ciphertext, tag)

assert test_message == decrypted
print("Encryption test passed")
'''],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Encryption works correctly")
        return True
    else:
        print(f"✗ Encryption test failed: {result.stderr}")
        return False


def test_storage():
    """Test storage module independently."""
    print("\nTesting storage module...")
    
    result = subprocess.run(
        ['python', '-c', '''
from storage import InMemoryStorage, SessionManager

storage = InMemoryStorage()
storage.add_message("User1", "Message 1")
storage.add_message("User2", "Message 2")

assert storage.get_count() == 2
storage.clear()
assert storage.get_count() == 0

manager = SessionManager()
session = manager.create_session("test")
session.add_message("User", "Test")
assert session.get_count() == 1

manager.clear_all()
print("Storage test passed")
'''],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Storage works correctly")
        return True
    else:
        print(f"✗ Storage test failed: {result.stderr}")
        return False


def main():
    """Run all tests."""
    print("=== TerminalChat Integration Tests ===\n")
    
    tests = [
        test_encryption,
        test_storage,
        test_server_startup,
        test_client_connection,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} raised exception: {e}")
            failed += 1
    
    print(f"\n{'='*40}")
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print(f"{'='*40}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
