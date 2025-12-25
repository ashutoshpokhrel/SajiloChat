
import socket
import threading
import json

IP_address = socket.gethostbyname(socket.gethostname())
Port = 5050
BufferSize = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server_socket.bind((IP_address, Port))
    server_socket.listen()
    print("=" * 60)
    print("         SAJILO CHAT SERVER")
    print("=" * 60)
    print(f"Server is listening on {IP_address}:{Port}")
    print("Waiting for connections...")
    print("=" * 60)
except OSError as e:
    print(f"Error binding to port: {e}")
    print("Try closing other instances or wait a minute")
    exit()

# Dictionary to store client connections: {username: socket}
clients = {}
clients_lock = threading.Lock()


def broadcast(message_data, exclude_user=None):
    """Send message to all connected clients except exclude_user"""
    with clients_lock:
        for username, client in clients.items():
            if username != exclude_user:
                try:
                    client.send(json.dumps(message_data).encode())
                except:
                    pass


def send_to_user(username, message_data):
    """Send message to a specific user"""
    with clients_lock:
        if username in clients:
            try:
                clients[username].send(json.dumps(message_data).encode())
                return True
            except:
                return False
        return False


def send_user_list():
    """Send updated user list to all clients"""
    with clients_lock:
        user_list = list(clients.keys())
    
    message_data = {
        'type': 'user_list',
        'users': user_list
    }
    broadcast(message_data)


def handle(client, username):
    """Handle messages from a client"""
    while True:
        try:
            message = client.recv(BufferSize)
            if not message:
                break
            
            # Parse the JSON message
            message_data = json.loads(message.decode())
            message_type = message_data.get('type')
            
            if message_type == 'group':
                # Group message - broadcast to everyone
                broadcast_data = {
                    'type': 'group',
                    'from': username,
                    'message': message_data.get('message')
                }
                broadcast(broadcast_data)
                print(f"[GROUP] {username}: {message_data.get('message')}")
                
            elif message_type == 'dm':
                # Direct message - send to specific user
                recipient = message_data.get('to')
                dm_data = {
                    'type': 'dm',
                    'from': username,
                    'message': message_data.get('message')
                }
                
                # Send to recipient
                if send_to_user(recipient, dm_data):
                    # Send confirmation back to sender
                    confirmation = {
                        'type': 'dm',
                        'from': username,
                        'to': recipient,
                        'message': message_data.get('message'),
                        'sent': True
                    }
                    client.send(json.dumps(confirmation).encode())
                    print(f"[DM] {username} -> {recipient}: {message_data.get('message')}")
                else:
                    # User not found or offline
                    error_data = {
                        'type': 'error',
                        'message': f'User {recipient} not found or offline'
                    }
                    client.send(json.dumps(error_data).encode())
                    print(f"[ERROR] {username} tried to DM offline user: {recipient}")
                    
            elif message_type == 'request_users':
                # Client is requesting the user list
                send_user_list()
                
        except Exception as e:
            print(f"[ERROR] Error handling message from {username}: {e}")
            break
    
    # Cleanup after loop ends
    with clients_lock:
        if username in clients:
            del clients[username]
            print(f"[DISCONNECT] {username} disconnected")
    
    # Notify others
    disconnect_data = {
        'type': 'system',
        'message': f'{username} left the chat'
    }
    broadcast(disconnect_data)
    
    # Send updated user list
    send_user_list()
    
    try:
        client.close()
    except:
        pass


def receive():
    """Accept new client connections"""
    while True:
        try:
            client, address = server_socket.accept()
            print(f"\n[CONNECTION] New connection from {str(address)}")
            
            # Ask for username
            client.send(json.dumps({'type': 'request_username'}).encode())
            username_msg = client.recv(BufferSize).decode()
            username_data = json.loads(username_msg)
            username = username_data.get('username')
            
            # Check if username is already taken
            with clients_lock:
                if username in clients:
                    error_data = {'type': 'error', 'message': 'Username already taken'}
                    client.send(json.dumps(error_data).encode())
                    client.close()
                    print(f"[REJECTED] Username '{username}' already taken")
                    continue
                
                clients[username] = client
            
            print(f"[LOGIN] Username: {username}")
            
            # Send welcome message
            welcome_data = {
                'type': 'system',
                'message': f'Welcome to the server, {username}!'
            }
            client.send(json.dumps(welcome_data).encode())
            
            # Notify others
            join_data = {
                'type': 'system',
                'message': f'{username} joined the chat'
            }
            broadcast(join_data, exclude_user=username)
            
            # Send updated user list to everyone
            send_user_list()
            
            # Start handling this client
            thread = threading.Thread(target=handle, args=(client, username))
            thread.start()
            
        except Exception as e:
            print(f"[ERROR] Error accepting connection: {e}")
            break


# Start the server
receive()



"""

"""