import socket
import threading
from config import *

SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    length = len(message)
    header = str(length).encode(FORMAT)
    header += b' ' * (HEADER - len(header))
    client.send(header)
    client.send(message)

def receive():
    while True:
        try:
            header = client.recv(HEADER).decode(FORMAT)
            if not header:
                break
            msg_length = int(header)
            msg = client.recv(msg_length).decode(FORMAT)
            print(msg)
        except:
            break

# ---------- AUTH ----------
choice = input("Login or Register (L/R): ").upper()
username = input("Username: ")
password = input("Password: ")

if choice == "R":
    auth_msg = f"REGISTER|{username}|{password}"
else:
    auth_msg = f"LOGIN|{username}|{password}"

client.send(auth_msg.encode(FORMAT))
response = client.recv(2048).decode(FORMAT)

if response.startswith("ERROR"):
    print(response)
    client.close()
    exit()

print("Authenticated!")

# ---------- CHAT ----------
threading.Thread(target=receive, daemon=True).start()

while True:
    msg = input()
    if msg == "exit":
        send(DISCONNECT_MESSAGE)
        break
    send(msg)
