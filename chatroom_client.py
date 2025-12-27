
import socket
import threading

HOST_IP= socket.gethostbyname(socket.gethostname())# ip of the laptop in the local router
Port= 5052
BufferSize=1024

# server side socket
client_socket= socket.socket(socket.AF_INET,socket.SOCK_STREAM)# ipv4 with tcp socket
address=(HOST_IP,Port)


Username= input("Enter your Username:")
# connecting the client socket to the server
client_socket.connect(address)

def receive():
    while True:
        try:
            message= client_socket.recv(BufferSize)
            if message.decode()=='Username':
                client_socket.send(Username.encode())
            else:
                print(message.decode())
            
        except:
            print("An error occured!!")
            client_socket.close()
            break

def write():
    while True:
        message = f'{Username}:{input("")}'
        client_socket.send(message.encode())


receive_thread= threading.Thread(target=receive)
receive_thread.start()


write_thread = threading.Thread(target=write)
write_thread.start()






























