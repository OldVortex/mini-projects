import socket
import threading

HOST = "127.0.0.1"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

print(f"Server listening on {HOST}:{PORT}")

def client_handler(client_socket, client_address):
    username = client_socket.recv(1024).decode()
    print(f"{username} connected from [{client_address[0]}:{client_address[1]}]")
    
    while True:
        message = client_socket.recv(1024).decode()
        
        if not message:
            print(f"Client [{client_address[0]}:{client_address[1]}] disconnected")
            break
        
        print(f"[{client_address[0]}:{client_address[1]}]: {message}")
        
        client_socket.send(message.encode())

    client_socket.close()

try:
    while True:
        client_socket, client_address = server.accept()
        print(f"Connected to {client_address}")
    
        thread = threading.Thread(
            target = client_handler,
            args = (client_socket, client_address)
        )
        
        thread.daemon = True
        thread.start()

except KeyboardInterrupt:
    print("/nShutting down server....")
    server.close()
