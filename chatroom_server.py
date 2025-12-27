import socket
import threading


# defining constants
IP_address=socket.gethostbyname(socket.gethostname())
Port=5052
Address=(IP_address,Port)
BufferSize=1024

# IPv4 with tcp connection
server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# binding ip_address and port
server_socket.bind((IP_address,Port))

# listening for incomming connextion
server_socket.listen()


clients=[]
usernames=[]

def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message= client.recv(BufferSize)
            broadcast(message)
# if it throws some exception, we cut the connection from the client terminate the loop.

        except:
            index= clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} Disconnected'.encode())
            usernames.remove(username)
            break


# for receiving the connection for the clients
def receive():
    # Never ending loop so that the server is always 
    while True:
        client,address = server_socket.accept()
        print(f'Connected with {str(address)}')

        client.send('Username'.encode()) # asking user for the n
        username = client.recv(BufferSize).decode()
        usernames.append(username)
        clients.append(client)

        print(f'Username of the client is{username}!')
        # this is shown in client server 
        broadcast(f'{username} joined the chat'.encode())
        client.send(f'Connected to the server'.encode())

        thread= threading.Thread(target=handle,args=(client,))
        thread.start()




print("Server is listening")

receive()










































