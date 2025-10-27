"""
Secure Terminal Chat Server
Handles multiple client connections with end-to-end encryption.
All data stored in memory only, no logging or disk persistence.
"""

import socket
import threading
import json
import base64
import signal
import sys
from encryption import SecureEncryption
from storage import SessionManager


class ChatServer:
    """
    Secure chat server that maintains end-to-end encryption.
    - No logging
    - All data in RAM
    - Automatic cleanup on exit
    """
    
    def __init__(self, host='127.0.0.1', port=9999):
        """
        Initialize chat server.
        Args:
            host: str - server host address
            port: int - server port
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {socket: {'id': anonymous_id, 'encryption': SecureEncryption}}
        self.clients_lock = threading.Lock()
        self.session_manager = SessionManager()
        self.running = False
        self.anonymous_counter = 0
        
        # Register cleanup on exit
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def generate_anonymous_id(self):
        """
        Generate anonymous identifier for client.
        Returns: str - anonymous ID like "Anonymous#0001"
        """
        with self.clients_lock:
            self.anonymous_counter += 1
            return f"Anonymous#{self.anonymous_counter:04d}"
    
    def start(self):
        """Start the chat server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"[SERVER] Secure chat server started on {self.host}:{self.port}")
        print("[SERVER] All data stored in memory only - no logging or persistence")
        print("[SERVER] Press Ctrl+C to shutdown and clear all data")
        
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
            except OSError:
                break
    
    def handle_client(self, client_socket):
        """
        Handle individual client connection.
        Args:
            client_socket: socket - client connection
        """
        anonymous_id = self.generate_anonymous_id()
        encryption = SecureEncryption()
        
        # Register client
        with self.clients_lock:
            self.clients[client_socket] = {
                'id': anonymous_id,
                'encryption': encryption
            }
        
        try:
            # Send server welcome and anonymous ID
            welcome_msg = {
                'type': 'welcome',
                'id': anonymous_id,
                'message': 'Connected to secure chat. All messages are encrypted and stored only in memory.'
            }
            self.send_message(client_socket, welcome_msg)
            
            print(f"[SERVER] {anonymous_id} connected")
            
            # Main message loop
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.process_message(client_socket, message)
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    print(f"[SERVER] Error processing message: {e}")
        
        except Exception as e:
            print(f"[SERVER] Client handler error: {e}")
        finally:
            self.disconnect_client(client_socket)
    
    def process_message(self, client_socket, message):
        """
        Process incoming client message.
        Args:
            client_socket: socket - client connection
            message: dict - message from client
        """
        msg_type = message.get('type')
        
        if msg_type == 'chat':
            # Broadcast encrypted message to all other clients
            self.broadcast_message(client_socket, message)
        elif msg_type == 'disconnect':
            self.disconnect_client(client_socket)
    
    def broadcast_message(self, sender_socket, message):
        """
        Broadcast message to all connected clients.
        Args:
            sender_socket: socket - sender's connection
            message: dict - message to broadcast
        """
        with self.clients_lock:
            sender_id = self.clients[sender_socket]['id']
            message['sender'] = sender_id
            
            for client_socket in list(self.clients.keys()):
                if client_socket != sender_socket:
                    try:
                        self.send_message(client_socket, message)
                    except:
                        pass
    
    def send_message(self, client_socket, message):
        """
        Send message to a client.
        Args:
            client_socket: socket - client connection
            message: dict - message to send
        """
        try:
            msg_json = json.dumps(message)
            client_socket.sendall(msg_json.encode('utf-8'))
        except Exception as e:
            print(f"[SERVER] Error sending message: {e}")
    
    def disconnect_client(self, client_socket):
        """
        Disconnect and cleanup client.
        Args:
            client_socket: socket - client connection
        """
        with self.clients_lock:
            if client_socket in self.clients:
                client_info = self.clients[client_socket]
                anonymous_id = client_info['id']
                
                # Clear encryption keys from memory
                client_info['encryption'].clear_keys()
                
                # Remove client
                del self.clients[client_socket]
                
                print(f"[SERVER] {anonymous_id} disconnected")
        
        try:
            client_socket.close()
        except:
            pass
    
    def shutdown(self, signum=None, frame=None):
        """
        Shutdown server and clear all data from memory.
        """
        print("\n[SERVER] Shutting down...")
        self.running = False
        
        # Disconnect all clients
        with self.clients_lock:
            for client_socket in list(self.clients.keys()):
                self.disconnect_client(client_socket)
        
        # Clear all sessions
        self.session_manager.clear_all()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("[SERVER] All data cleared from memory")
        sys.exit(0)


def main():
    """Main entry point for server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Secure Terminal Chat Server')
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=9999, help='Server port (default: 9999)')
    
    args = parser.parse_args()
    
    server = ChatServer(host=args.host, port=args.port)
    server.start()


if __name__ == '__main__':
    main()
