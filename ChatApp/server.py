import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5555

def timestamp():
    return time.strftime("%H:%M:%S")


clients = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print(f"/nServer listening on {HOST}:{PORT}")

def client_handler(client_socket, client_address):
    username = client_socket.recv(1024).decode()
    print(f"/n[{timestamp()}] [CONNECTED] {username} ({client_address[0]}:{client_address[1]})")
    clients.append(client_socket)
    
    while True:
        message = client_socket.recv(1024).decode()
        
        if not message:
            print(f"/n[{timestamp()}] [DISCONNECTED] {username}")
            clients.remove(client_socket)
            break
        
        print(f"/n[{timestamp()}] [MESSAGE] {username}: {message}")
        
        client_socket.send(message.encode())

    client_socket.close()

try:
    while True:
        client_socket, client_address = server.accept()
    
        thread = threading.Thread(
            target = client_handler,
            args = (client_socket, client_address)
        )

        thread.start()

except KeyboardInterrupt:
    print("/nShutting down server....")
    server.close()
