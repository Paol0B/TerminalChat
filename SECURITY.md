# Security Overview - TerminalChat

This document details the security architecture and guarantees of TerminalChat.

## Security Requirements Met

### ✅ Full Anonymity
- **No User Registration**: Users connect without providing any identifying information
- **Anonymous IDs**: Server automatically assigns anonymous identifiers (e.g., "Anonymous#0001")
- **No IP Logging**: No connection logs or IP address storage
- **Ephemeral Identity**: Anonymous ID is only valid for the current session

### ✅ End-to-End Encryption

#### Hybrid Encryption Approach
The application uses a hybrid encryption system combining asymmetric and symmetric cryptography:

1. **RSA 2048-bit** - For secure key exchange
   - Each client generates a unique RSA key pair on connection
   - Public keys can be exchanged safely over the network
   - Private keys never leave the client's memory

2. **AES-256-GCM** - For message encryption
   - Fast symmetric encryption for message content
   - Galois/Counter Mode (GCM) provides authenticated encryption
   - Unique initialization vector (IV) for each message
   - Authentication tags prevent tampering

#### Encryption Flow
```
Client A                    Server                    Client B
--------                    ------                    --------
Generate RSA keypair                                  Generate RSA keypair
    |                                                     |
    +---------------> Exchange public keys <-------------+
    |                                                     |
Generate AES session key                                 |
    |                                                     |
Encrypt with B's RSA key ---> Relay encrypted key ----> Decrypt with private key
    |                                                     |
Encrypt message with AES                                 |
    |                                                     |
Send encrypted message ------> Relay message ---------> Decrypt with AES key
```

### ✅ Memory-Only Storage

#### In-Memory Data Structures
- **Thread-Safe Deques**: Messages stored in `collections.deque` with automatic size limiting
- **No Disk I/O**: Zero file operations for message or key storage
- **Automatic Cleanup**: All data structures cleared on exit via signal handlers

#### What's Stored in Memory
- Active client connections (socket objects)
- Anonymous identifiers (session-specific)
- Encryption keys (automatically cleared)
- Recent messages (limited to prevent memory overflow)

#### What's NEVER Stored
- User credentials (none required)
- Chat history beyond current session
- Connection logs
- IP addresses
- Encryption keys after disconnect

### ✅ No Logging or Persistence

#### Zero Logging Policy
```python
# No file operations like these exist in the codebase:
# ❌ logging.FileHandler()
# ❌ open('log.txt', 'w')
# ❌ with open('messages.db', 'w')
```

#### No Persistence Mechanisms
- No database connections
- No file writes
- No swap usage (best effort)
- No cache files
- No temporary files for messages

### ✅ Easy to Use

#### Simple Installation
```bash
pip install -r requirements.txt  # Only cryptography library
```

#### Simple Usage
```bash
# Server
python server.py

# Client
python client.py
```

No configuration files, no setup wizards, no user accounts.

## Security Architecture

### Threat Model

#### What We Protect Against
- **Passive Network Eavesdropping**: All messages encrypted in transit
- **Message Tampering**: GCM authentication prevents modification
- **Post-Session Data Recovery**: No disk persistence to recover
- **User Tracking**: Anonymous IDs with no persistent identity
- **Forensic Analysis**: Memory-only storage leaves no trace after exit

#### What We Don't Protect Against
- **Active MitM with Server Control**: Server could be modified to log
- **Compromised Endpoints**: Malware on client or server
- **Memory Forensics on Running System**: RAM can be dumped if system compromised
- **Traffic Analysis**: Connection patterns visible (use Tor for network anonymity)
- **Denial of Service**: Basic server with no DoS protection

### Cryptographic Details

#### Key Sizes
- RSA: 2048 bits (considered secure through 2030+)
- AES: 256 bits (quantum-resistant for foreseeable future)
- IV: 96 bits (recommended for GCM)
- Session Key: 256 bits random

#### Random Number Generation
- Uses `os.urandom()` for cryptographically secure randomness
- Sources: `/dev/urandom` on Unix, `CryptGenRandom` on Windows

#### Key Management
```python
# Keys are generated per-session
private_key = rsa.generate_private_key(...)
session_key = os.urandom(32)

# Keys are cleared on exit
def clear_keys(self):
    self.private_key = None
    self.public_key = None
    self.session_key = None
```

### Network Security

#### Transport Layer
- Uses TCP sockets (not encrypted at transport layer)
- Messages encrypted at application layer
- Consider these additions for production:
  - TLS/SSL for transport encryption
  - Tor for network anonymity
  - VPN for IP protection

#### Message Format
Messages are JSON-encoded with encrypted payloads:
```json
{
  "type": "chat",
  "sender": "Anonymous#0001",
  "content": "<encrypted_message>",
  "iv": "<base64_iv>",
  "tag": "<base64_tag>"
}
```

## Security Best Practices

### For Users

1. **Trusted Network**
   - Use on private networks or over VPN
   - Don't expose server to public internet without additional protection

2. **Secure Environment**
   - Run on trusted hardware
   - Use full disk encryption
   - Ensure system is malware-free

3. **Network Anonymity**
   - Use Tor for additional anonymity
   - VPN for IP protection
   - Consider running over I2P or similar

4. **Clean Exit**
   - Always exit cleanly (Ctrl+C or `/quit`)
   - Ensures proper memory cleanup

### For Administrators

1. **Server Hardening**
   - Run on trusted infrastructure
   - Firewall the server port
   - Regular security updates
   - Monitor for unusual activity

2. **Network Security**
   - Use private networks when possible
   - Consider adding TLS/SSL
   - Implement rate limiting
   - Add IP filtering if needed

3. **Code Verification**
   - Review source code before deployment
   - Verify cryptography library version
   - Check for unauthorized modifications
   - Regular security audits

## Security Limitations

### Known Limitations

1. **Server Trust Required**
   - Server relays all messages
   - Could be modified to log (though current code doesn't)
   - Consider peer-to-peer for zero-trust

2. **Memory Security**
   - Running process memory can be dumped
   - OS may swap memory to disk
   - Use encrypted RAM or disable swap

3. **No Perfect Forward Secrecy**
   - Session keys persist for entire session
   - If key compromised, all session messages affected
   - Future enhancement: rotate session keys

4. **No Authentication**
   - Anyone can connect if they know host:port
   - No way to verify identity of peers
   - By design for anonymity

5. **Basic DoS Protection**
   - No rate limiting
   - No connection limits
   - No message size limits (beyond socket buffer)

## Compliance & Legal

### Privacy Guarantees
- No PII (Personally Identifiable Information) collected
- No data retention
- No third-party data sharing
- No analytics or tracking

### Use Cases
Appropriate for:
- Privacy-focused communication
- Ephemeral group chats
- Secure coordination
- Anonymous discussions

Not appropriate for:
- Legal record keeping
- Audit trail requirements
- Long-term communication history
- High-assurance authentication needs

### Legal Disclaimer
- Software provided as-is
- Users responsible for legal compliance
- Encryption laws vary by jurisdiction
- Review local laws before use

## Security Maintenance

### Dependency Management
```bash
# Check for vulnerabilities
pip list --outdated

# Update cryptography library
pip install --upgrade cryptography
```

### Security Updates
- Monitor cryptography library security advisories
- Update Python to latest stable version
- Review code changes before updates
- Test after security updates

### Incident Response
If security issue discovered:
1. Stop affected servers immediately
2. Review logs (if any exist)
3. Update to patched version
4. Notify users to clear memory/restart
5. Consider key rotation

## Security Testing

### Automated Tests
```bash
python test_integration.py  # Run integration tests
```

### Manual Security Testing
1. **Encryption Test**: Verify messages are encrypted
2. **Memory Test**: Verify no disk writes during operation
3. **Clean Exit Test**: Verify memory cleared on exit
4. **Connection Test**: Verify anonymous IDs assigned
5. **Network Test**: Verify no plaintext message transmission

### Security Audit Checklist
- [ ] All dependencies up to date
- [ ] No known CVEs in dependencies
- [ ] No file I/O operations for messages
- [ ] Memory cleared on exit
- [ ] Encryption keys properly generated
- [ ] No logging code present
- [ ] Anonymous IDs properly assigned

## Future Security Enhancements

### Planned Improvements
1. **Perfect Forward Secrecy**: Rotate session keys periodically
2. **Peer-to-Peer**: Remove server as central point
3. **Tor Integration**: Built-in network anonymity
4. **Multi-Party Computation**: Advanced group chat encryption
5. **Voice/Video**: Encrypted real-time communication
6. **File Transfer**: Encrypted file sharing (memory-only)

### Research Directions
- Zero-knowledge proofs for authentication
- Post-quantum cryptography
- Steganography for traffic obfuscation
- Distributed hash table for decentralized coordination

---

**Remember**: No security system is perfect. Use TerminalChat as part of a comprehensive security strategy that includes operational security, trusted infrastructure, and appropriate threat modeling.

For questions or security concerns, please review the source code or consult with a security professional.
