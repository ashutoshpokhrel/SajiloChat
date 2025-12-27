import socket
import threading
import json
import sys
import time

HOST_IP = socket.gethostbyname(socket.gethostname())
Port = 5050
BufferSize = 1024

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (HOST_IP, Port)

# Get username
print("=" * 50)
print("         SAJILO CHAT - Python Client")
print("=" * 50)
Username = input("Enter your Username: ")

try:
    client_socket.connect(address)
    print(f"Connecting to {HOST_IP}:{Port}...")
except Exception as e:
    print(f"Could not connect to server: {e}")
    sys.exit()

# Global variables
running = True
online_users = []
current_chat = None  # None = group chat, username = DM
handshake_complete = threading.Event()


def display_help():
    print("\n" + "=" * 50)
    print("COMMANDS:")
    print("  /users          - Show online users")
    print("  /dm <username>  - Start DM with user")
    print("  /group          - Return to group chat")
    print("  /menu           - Return to main menu")
    print("  /help           - Show this help")
    print("  /quit           - Exit chat")
    print("=" * 50 + "\n")


def display_header():
    if current_chat is None:
        print("\n" + "=" * 50)
        print("           GROUP CHAT")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print(f"        DIRECT MESSAGE with {current_chat}")
        print("=" * 50)


def display_main_menu():
    print("\n" + "=" * 50)
    print("           MAIN MENU")
    print("=" * 50)
    print("1. Group Chat")
    print("2. Direct Message (DM)")
    print("3. View Online Users")
    print("4. Help")
    print("5. Exit")
    print("=" * 50)


def show_online_users():
    print("\n" + "=" * 50)
    print("ONLINE USERS:")
    if len(online_users) <= 1:
        print("  (No other users online)")
    else:
        for user in online_users:
            if user != Username:
                print(f"  • {user}")
    print("=" * 50 + "\n")


def choose_dm_user():
    available_users = [u for u in online_users if u != Username]
    
    if not available_users:
        print("\n[No other users online to DM]")
        return None
    
    print("\n" + "=" * 50)
    print("SELECT USER TO DM:")
    for idx, user in enumerate(available_users, 1):
        print(f"{idx}. {user}")
    print("0. Cancel")
    print("=" * 50)
    
    while True:
        try:
            choice = input("Enter number: ").strip()
            if choice == '0':
                return None
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_users):
                return available_users[choice_idx]
            else:
                print("[Invalid choice. Try again.]")
        except ValueError:
            print("[Please enter a number.]")


def receive():
    global running, online_users, current_chat
    
    while running:
        try:
            message = client_socket.recv(BufferSize)
            if not message:
                print("\n[Server closed the connection]")
                running = False
                break
            
            data = json.loads(message.decode())
            msg_type = data.get('type')
            
            if msg_type == 'request_username':
                response = json.dumps({'username': Username})
                client_socket.send(response.encode())
                
            elif msg_type == 'system':
                system_msg = data.get('message')
                print(f"\n[SYSTEM] {system_msg}")
                if 'Welcome' in system_msg or 'server' in system_msg.lower():
                    handshake_complete.set()
                
            elif msg_type == 'user_list':
                online_users = data.get('users', [])
                print(f"\n[{len(online_users)} users online]")
                
            elif msg_type == 'group':
                if current_chat is None:
                    sender = data.get('from')
                    message = data.get('message')
                    print(f"\n{sender}: {message}")
                    
            elif msg_type == 'dm':
                sender = data.get('from')
                message = data.get('message')
                
                if sender == Username:
                    recipient = data.get('to')
                    if current_chat == recipient:
                        print(f"\nYou: {message}")
                else:
                    if current_chat == sender:
                        print(f"\n{sender}: {message}")
                    else:
                        print(f"\n[DM from {sender}]: {message}")
                        print(f"[Type '/dm {sender}' to reply or go to Main Menu]")
                        
            elif msg_type == 'error':
                print(f"\n[ERROR] {data.get('message')}")
                
        except json.JSONDecodeError:
            print("\n[Error decoding message]")
        except Exception as e:
            if running:
                print(f"\n[Connection error: {e}]")
            running = False
            break
    
    try:
        client_socket.close()
    except:
        pass


def handle_menu():
    global running, current_chat
    
    handshake_complete.wait()
    time.sleep(0.3)
    
    while running:
        display_main_menu()
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            current_chat = None
            display_header()
            print("Entered group chat")
            display_help()
            chat_loop()
            
        elif choice == '2':
            target_user = choose_dm_user()
            if target_user:
                current_chat = target_user
                display_header()
                print(f"Started DM with {target_user}")
                display_help()
                chat_loop()
            
        elif choice == '3':
            show_online_users()
            
        elif choice == '4':
            display_help()
            
        elif choice == '5':
            print("\nDisconnecting...")
            running = False
            break
            
        else:
            print("\n[Invalid choice. Please enter 1-5]")


def chat_loop():
    global running, current_chat
    
    while running:
        try:
            if current_chat is None:
                prompt = f"{Username} (Group): "
            else:
                prompt = f"{Username} -> {current_chat}: "
            
            user_input = input(prompt)
            
            if not user_input.strip():
                continue
            
            if user_input.startswith('/'):
                command = user_input.split()
                cmd = command[0].lower()
                
                if cmd == '/quit':
                    print("Disconnecting...")
                    running = False
                    break
                    
                elif cmd == '/menu':
                    print("Returning to main menu...\n")
                    return
                    
                elif cmd == '/help':
                    display_help()
                    
                elif cmd == '/users':
                    show_online_users()
                    
                elif cmd == '/group':
                    current_chat = None
                    display_header()
                    print("Switched to group chat\n")
                    
                elif cmd == '/dm':
                    if len(command) < 2:
                        print("[Usage: /dm <username>]")
                    else:
                        target_user = command[1]
                        if target_user == Username:
                            print("[You cannot DM yourself!]")
                        elif target_user in online_users:
                            current_chat = target_user
                            display_header()
                            print(f"Switched to DM with {target_user}\n")
                        else:
                            print(f"[User '{target_user}' not found or offline]")
                            
                else:
                    print(f"[Unknown command: {cmd}]")
                    print("[Type /help for available commands]")
                    
                continue
            
            if current_chat is None:
                message_data = {
                    'type': 'group',
                    'message': user_input
                }
            else:
                message_data = {
                    'type': 'dm',
                    'to': current_chat,
                    'message': user_input
                }
            
            client_socket.send(json.dumps(message_data).encode())
            
        except KeyboardInterrupt:
            print("\nReturning to menu...")
            return
        except Exception as e:
            if running:
                print(f"\n[Error sending message: {e}]")
            return


receive_thread = threading.Thread(target=receive, daemon=True)
receive_thread.start()

try:
    handle_menu()
except KeyboardInterrupt:
    print("\n\nDisconnecting...")
    running = False

running = False
try:
    client_socket.close()
except:
    pass

print("\n" + "=" * 50)
print("         Disconnected from server")
print("=" * 50)