import socket
import threading
from config import *
from auth import authenticate
from database import init_db

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []

def send_message(conn, msg):
    message = msg.encode(FORMAT)
    length = len(message)
    header = str(length).encode(FORMAT)
    header += b' ' * (HEADER - len(header))
    conn.send(header)
    conn.send(message)

def broadcast(msg, sender=None):
    for client, _ in clients:
        if client != sender:
            send_message(client, msg)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    username = None

    try:
        # ---- AUTH ----
        auth_data = conn.recv(1024).decode(FORMAT)

        parts = auth_data.split("|")
        if len(parts) != 3:
            conn.send("ERROR|Invalid auth format".encode(FORMAT))
            conn.close()
            return

        action, username, password = parts


        token, error = authenticate(action, username, password)

        if error:
            conn.send(f"ERROR|{error}".encode())
            conn.close()
            return

        conn.send(f"TOKEN|{token}".encode())

        clients.append((conn, username))
        broadcast(f"[SERVER] {username} joined the chat")

        while True:
            header = conn.recv(HEADER).decode(FORMAT)
            if not header:
                break

            msg_length = int(header)
            msg = conn.recv(msg_length).decode(FORMAT)

            if msg == DISCONNECT_MESSAGE:
                break

            broadcast(f"{username}: {msg}", conn)

    finally:
        print(f"[DISCONNECTED] {username}")
        for c in clients:
            if c[0] == conn:
                clients.remove(c)
                break
        broadcast(f"[SERVER] {username} left the chat")
        conn.close()

def start():
    init_db()
    server.listen()
    print(f"[LISTENING] {SERVER}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print("[STARTING] Server starting...")
start()
