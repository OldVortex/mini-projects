import socket

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen(1)

print(f"Server listening on {HOST}:{PORT}")

client_socket, client_address = server.accept()

print(f"Connected to {client_address}")

message = client_socket.recv(1024).decode()

print(f"Received: {message}")

client_socket.close()
server.close()
