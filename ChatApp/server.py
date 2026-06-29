import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5555

clients = {}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

def timestamp():
    return time.strftime("%H:%M:%S")

def broadcast(message, sender = None):
    for client in list(clients):
        if client != sender:
            try:
                client.send(message.encode())
            except:
                pass

def send_private_msg(sender, recipient, message):
    for client, username in clients.items():
        if username.lower() == recipient.lower():
            client.send(f"[PM] {sender}: {message}".encode())
            return True
    
    return False

print(f"\nServer listening on {HOST}:{PORT}\n")

def username_check(username):
    return username.lower() in (name.lower() for name in clients.values())

def client_handler(client_socket, client_address):
    
    try:
        username = client_socket.recv(1024).decode()
        
        if not username:
            client_socket.close()
            return
        
        if username_check(username):
            client_socket.send("Username already taken.".encode())
            client_socket.close()
            return
        
        client_socket.send("OK".encode())
        
        print(f"[{timestamp()}] [CONNECTED] {username} ({client_address[0]}:{client_address[1]})")
        
        clients[client_socket] = username
        
        while True:
            message = client_socket.recv(1024).decode()
            
            if message.startswith("/msg"):
                parts = message.split(" ", 2)
                
                if len(parts) < 3:
                    client_socket.send("Usage: /msg <user> <message>\n".encode())
                    continue
            
                recipient = parts[1]
                private_msg = parts[2]
            
                print(f"[{timestamp()}] [PM] {username} -> {recipient}")
            
                success = send_private_msg(username, recipient, private_msg)
                
                if not success:
                    client_socket.send(f"User '{recipient}' not found.".encode())
                
                continue
            
            if not message:
                break
            
            print(f"[{timestamp()}] [MESSAGE] {username}: {message}")
            
            broadcast(f"{username}: {message}", sender = client_socket)
    
    except ConnectionResetError:
        pass
    
    finally:
        print(f"[{timestamp()}] [DISCONNECTED] {username}")
        clients.pop(client_socket, None)
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
    print("\nShutting down server....")
    server.close()
