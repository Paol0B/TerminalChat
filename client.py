"""
Secure Terminal Chat Client
Connects to chat server with end-to-end encryption.
Anonymous communication with no data persistence.
"""

import socket
import threading
import json
import sys
import signal
from encryption import SecureEncryption


class ChatClient:
    """
    Secure chat client with end-to-end encryption.
    - Anonymous by default
    - All data in memory only
    - No logging
    """
    
    def __init__(self, host='127.0.0.1', port=9999):
        """
        Initialize chat client.
        Args:
            host: str - server host
            port: int - server port
        """
        self.host = host
        self.port = port
        self.socket = None
        self.encryption = SecureEncryption()
        self.anonymous_id = None
        self.running = False
        self.receive_thread = None
        
        # Register cleanup on exit
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def connect(self):
        """Connect to the chat server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            return False
    
    def receive_messages(self):
        """Receive and process messages from server."""
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self.process_message(message)
            except json.JSONDecodeError:
                pass
            except Exception as e:
                if self.running:
                    print(f"[ERROR] Receive error: {e}")
                break
        
        if self.running:
            print("\n[INFO] Connection lost")
            self.running = False
    
    def process_message(self, message):
        """
        Process incoming message from server.
        Args:
            message: dict - message from server
        """
        msg_type = message.get('type')
        
        if msg_type == 'welcome':
            self.anonymous_id = message.get('id')
            print(f"\n{message.get('message')}")
            print(f"Your anonymous ID: {self.anonymous_id}")
            print("\nType your message and press Enter to send")
            print("Type '/quit' to exit\n")
        elif msg_type == 'chat':
            sender = message.get('sender', 'Unknown')
            content = message.get('content', '')
            print(f"\n{sender}: {content}")
            print("> ", end='', flush=True)
    
    def send_message(self, content):
        """
        Send message to server.
        Args:
            content: str - message content
        """
        try:
            message = {
                'type': 'chat',
                'content': content
            }
            msg_json = json.dumps(message)
            self.socket.sendall(msg_json.encode('utf-8'))
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
    
    def run(self):
        """Main client loop for user input."""
        if not self.connect():
            return
        
        try:
            while self.running:
                try:
                    print("> ", end='', flush=True)
                    message = input()
                    
                    if message.lower() == '/quit':
                        break
                    
                    if message.strip():
                        self.send_message(message)
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        finally:
            self.shutdown()
    
    def shutdown(self, signum=None, frame=None):
        """
        Shutdown client and clear data from memory.
        """
        if not self.running:
            return
        
        print("\n[INFO] Disconnecting...")
        self.running = False
        
        # Notify server of disconnect
        try:
            disconnect_msg = {'type': 'disconnect'}
            msg_json = json.dumps(disconnect_msg)
            self.socket.sendall(msg_json.encode('utf-8'))
        except:
            pass
        
        # Clear encryption keys
        self.encryption.clear_keys()
        
        # Close socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("[INFO] All data cleared from memory")
        sys.exit(0)


def main():
    """Main entry point for client."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Secure Terminal Chat Client')
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9999, help='Server port (default: 9999)')
    
    args = parser.parse_args()
    
    print("=== Secure Terminal Chat ===")
    print("Fully anonymous, end-to-end encrypted")
    print("All data stored in memory only")
    print("============================\n")
    
    client = ChatClient(host=args.host, port=args.port)
    client.run()


if __name__ == '__main__':
    main()
