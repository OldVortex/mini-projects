import socket
import threading

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print(f"Server listening on {HOST}:{PORT}")

def client_handler(client_socket):
    while True:
        message = client_socket.recv(1024).decode()
        
        if not message:
            print("Client Disconnected.")
            break
        
        client_socket.send(message.encode())
        print(f"Client: {message}")

    client_socket.close()

while True:
    client_socket, client_address = server.accept()
    print(f"Connected to {client_address}")
    
    thread = threading.Thread(
        target = client_handler,
        args = (client_socket,)
    )
    thread.start()

server.close()
