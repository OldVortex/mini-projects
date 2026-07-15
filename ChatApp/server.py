import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5555

history = []
clients = {}

clients_lock = threading.lock()
history_lock = threading.lock()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen()

def timestamp():
    return time.strftime("%H:%M:%S")

def broadcast(message, sender = None):
    with clients_lock:
        current_clients = list(clients)
        
    for client in current_clients:
        if client != sender:
            try:
                client.send(message.encode())
            except:
                pass

def send_private_msg(sender, recipient, message):
    with clients_lock:
        current_clients = list(clients.items())
    
    for client, username in current_clients:
        if username.lower() == recipient.lower():
            client.send(f"[PM] {sender}: {message}".encode())
            return True
    
    return False

print(f"\nServer listening on {HOST}:{PORT}\n")

def username_check(username):
    with clients_lock:
        return username.lower() in (name.lower() for name in clients.values())

def command_handler(client_socket, username, message):
    if message == "/users":
        with clients_lock:
            current_clients = list(clients.values())
            online = "\n".join(f"• {user}" for user in current_clients)
        
        client_socket.send(f"Online users:\n{online}".encode())
        print(f"[{timestamp()}] [COMMAND] {username}: /users")
        
        return True
    
    if message.startswith("/msg "):
        parts = message.split(" ", 2)
        
        if len(parts) < 3:
            client_socket.send("Usage: /msg <user> <message>".encode())      
            return True
        
        recipient = parts[1]
        private_msg = parts[2]
        
        print(f"[{timestamp()}] [PM] {username} -> {recipient}")
        
        success = send_private_msg(username, recipient, private_msg)
        
        if not success:
            client_socket.send(f"User '{recipient}' not found".encode())
            
        return True
    
    if message == "/help":
        help_text = ("Available commands:\n"
                     "/users - List of users\n"
                     "/msg <user> <message> - Send private message\n")
        
        client_socket.send(help_text.encode())
        print(f"[{timestamp()}] [COMMAND] {username}: /help")
        
        return True

    return False

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
        
        with clients_lock:
            clients[client_socket] = username
        
        broadcast(f"[{timestamp()}] [SERVER] {username} joined.")
        
        with history_lock:
            messages = history.copy()
            
        if messages:
            client_socket.send("------ Recent Messages -----\n".encode())
            
            for msg in messages:
                client_socket.send(f"{msg}\n".encode())
            
            client_socket.send("----------------------------\n".encode())
        
        while True:
            message = client_socket.recv(1024).decode()
            
            if not message:
                break
            
            if command_handler(client_socket, username, message):
                continue
            
            formatted = f"[{timestamp()}] [MESSAGE] {username}: {message}"
            with history_lock:
                history.append(formatted)
            
                if len(history) > 20:
                    history.pop(0)
            
            print(formatted)
            broadcast(formatted, sender = client_socket)
    
    except ConnectionResetError:
        pass
    
    finally:
        broadcast(f"[{timestamp()}] [SERVER] {username} has left.")
        print(f"[{timestamp()}] [DISCONNECTED] {username}")
        
        with clients_lock:
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
    
    with clients_lock:
        current_clients = list(clients)
    
    for client in current_clients:
        client.close()
        
    server.close()
