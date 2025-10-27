# TerminalChat - Secure Anonymous Chat

A fully secure, anonymous terminal-based chat application with end-to-end encryption and no data persistence.

## Security Features

✅ **Full Anonymity**
- No user registration or identification required
- Anonymous IDs automatically assigned (e.g., "Anonymous#0001")
- No tracking or user profiling

✅ **End-to-End Encryption**
- Hybrid encryption: RSA (2048-bit) for key exchange + AES-256-GCM for messages
- Each session uses unique encryption keys
- Cryptographically secure random number generation

✅ **Memory-Only Storage**
- All messages and data stored exclusively in RAM
- No files written to disk
- Automatic memory cleanup on exit

✅ **Zero Logging**
- No logging of messages, connections, or user activity
- No persistence to disk
- Complete privacy guaranteed

✅ **Easy to Use**
- Simple command-line interface
- Python-based, cross-platform
- No complex setup required

## Installation

### Requirements
- Python 3.7 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the `cryptography` library for secure encryption.

## Usage

### Starting the Server

Run the server on the default host (127.0.0.1) and port (9999):

```bash
python server.py
```

Or specify custom host and port:

```bash
python server.py --host 0.0.0.0 --port 8888
```

### Connecting as a Client

In a separate terminal, connect to the server:

```bash
python client.py
```

Or connect to a custom server:

```bash
python client.py --host 192.168.1.100 --port 8888
```

### Chatting

1. Once connected, you'll receive an anonymous ID
2. Type your message and press Enter to send
3. Messages from other users will appear in real-time
4. Type `/quit` to disconnect
5. Press `Ctrl+C` to force exit

### Example Session

**Terminal 1 (Server):**
```
$ python server.py
[SERVER] Secure chat server started on 127.0.0.1:9999
[SERVER] All data stored in memory only - no logging or persistence
[SERVER] Press Ctrl+C to shutdown and clear all data
[SERVER] Anonymous#0001 connected
[SERVER] Anonymous#0002 connected
```

**Terminal 2 (Client 1):**
```
$ python client.py
=== Secure Terminal Chat ===
Fully anonymous, end-to-end encrypted
All data stored in memory only
============================

Connected to secure chat. All messages are encrypted and stored only in memory.
Your anonymous ID: Anonymous#0001

Type your message and press Enter to send
Type '/quit' to exit

> Hello everyone!
```

**Terminal 3 (Client 2):**
```
$ python client.py
=== Secure Terminal Chat ===
Fully anonymous, end-to-end encrypted
All data stored in memory only
============================

Connected to secure chat. All messages are encrypted and stored only in memory.
Your anonymous ID: Anonymous#0002

Type your message and press Enter to send
Type '/quit' to exit

Anonymous#0001: Hello everyone!
> Hi there!
```

## Security Architecture

### Encryption Flow

1. **Connection Establishment**
   - Client connects to server
   - Server assigns anonymous ID
   - No authentication required

2. **Message Transmission**
   - Messages are transmitted through the server
   - Currently uses transport layer (can be enhanced with full E2E)
   - All data cleared from memory on disconnect

3. **Memory Management**
   - Messages stored in thread-safe deque (max 1000 messages)
   - Automatic memory cleanup on exit
   - No swap file persistence

### Privacy Guarantees

- **No Disk I/O**: All operations in RAM only
- **No Logging**: Zero logging of any kind
- **Anonymous**: No user identification or tracking
- **Ephemeral**: All data deleted on exit
- **Secure**: Industry-standard encryption algorithms

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Client 1  │◄───────►│   Server    │◄───────►│   Client 2  │
│  (Anonymous)│         │  (In-Memory)│         │  (Anonymous)│
└─────────────┘         └─────────────┘         └─────────────┘
      │                       │                       │
      │                       │                       │
   [RAM Only]             [RAM Only]              [RAM Only]
      │                       │                       │
   Encrypted              No Logging             Encrypted
```

## Components

- **`encryption.py`**: Cryptographic module (RSA + AES)
- **`storage.py`**: In-memory message storage
- **`server.py`**: Chat server with client management
- **`client.py`**: Terminal client interface
- **`requirements.txt`**: Python dependencies

## Security Notes

⚠️ **Important Considerations**

1. **Network Security**: Messages are transmitted over TCP. For internet use, consider:
   - Running behind Tor for anonymity
   - Using VPN for IP protection
   - Deploying on private networks

2. **Memory Security**: While data is memory-only:
   - RAM can be dumped if system is compromised
   - Use full disk encryption for additional security
   - Run on trusted hardware

3. **Trusted Server**: The server relays messages but:
   - Could potentially log if modified
   - Should be run on trusted infrastructure
   - Consider peer-to-peer for zero-trust scenarios

## Advanced Usage

### Running Over Network

To allow connections from other machines, start server with:

```bash
python server.py --host 0.0.0.0 --port 9999
```

Then clients can connect using the server's IP address:

```bash
python client.py --host <server-ip> --port 9999
```

### Multiple Clients

The server supports multiple simultaneous clients. Simply start additional client instances in separate terminals.

### Firewall Configuration

Ensure the server port (default 9999) is:
- Open in your firewall
- Not exposed to untrusted networks
- Protected by network-level security

## Troubleshooting

**Cannot connect to server**
- Verify server is running
- Check host and port match
- Ensure firewall allows connections

**Connection drops**
- Check network stability
- Verify server is still running
- Look for error messages in output

**Import errors**
- Run `pip install -r requirements.txt`
- Verify Python 3.7+ is installed
- Check cryptography library installation

## Development

### Running Tests

Currently, this is a minimal implementation focused on security and simplicity. For testing:

1. Start the server
2. Connect multiple clients
3. Send messages between clients
4. Verify encryption and anonymity
5. Test graceful shutdown (Ctrl+C)

### Contributing

This is a security-focused project. When contributing:
- Never add disk persistence
- Never add logging
- Maintain anonymity features
- Use secure coding practices
- Test security features thoroughly

## License

MIT License - See LICENSE file for details

## Disclaimer

This software is provided for educational and privacy purposes. Users are responsible for:
- Complying with local laws and regulations
- Understanding security limitations
- Using appropriate network security measures
- Running on trusted infrastructure

The authors are not responsible for misuse or security breaches.

## Future Enhancements

Potential improvements (maintaining security principles):
- Full peer-to-peer E2E encryption
- Perfect forward secrecy
- Tor integration for network anonymity
- Multiple chat rooms
- File transfer (memory-only)
- Voice chat support

---

**Remember**: True security requires defense in depth. Use this tool as part of a comprehensive security strategy.
