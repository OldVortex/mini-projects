import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5555

history = []
clients = {}

rooms = {
    "general",
    "music"
}

clients_lock = threading.Lock()
history_lock = threading.Lock()

def timestamp():
    return time.strftime("%H:%M:%S")

def broadcast(message, room, sender = None):
    with clients_lock:
        current_clients = list(clients.items())
        
    for client, info in current_clients:
        if client == sender:
            continue
        
        if info['room'] != room:
            continue
            
        try:
            client.send(message.encode())
        except:
            pass

def send_private_msg(sender, recipient, message):
    with clients_lock:
        current_clients = list(clients.items())
    
    for client, info in current_clients:
        if info["username"].lower() == recipient.lower():
            client.send(f"[PM] {sender}: {message}".encode())
            return True
    
    return False

def command_handler(client_socket, username, message):
    curr_room = clients[client_socket]["room"]
    
    if message == "/users":
        with clients_lock:
            current_clients = list(clients.values())
            
            online = []
            
            for info in current_clients:
                if info['room'] == curr_room:
                    online.append(f"• {info['username']}")
            
            online = "\n".join(online)
        
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
    username = None
    
    try:
        #Username Check
        username = client_socket.recv(1024).decode()
        
        if not username:
            client_socket.close()
            return
        
        with clients_lock:
            if username.lower() in (info["username"].lower() for info in clients.values()):
                client_socket.send("Username already taken.".encode())
                client_socket.close()
                return
            
            clients[client_socket] = {
                "username": username,
                "room": "general"
            }
        
        client_socket.send("OK".encode())
        
        room = clients[client_socket]['room']
        
        print(f"[{timestamp()}] [CONNECTED] {username} ({client_address[0]}:{client_address[1]})")
        
        broadcast(f"[{timestamp()}] [SERVER] {username} joined.", room)
        
        with history_lock:
            messages = history.copy()
        
        if messages:
            client_socket.send("\n------ Recent Messages -----\n".encode())
            
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
            broadcast(formatted, room, sender = client_socket)
    
    except ConnectionResetError:
        pass
    
    finally:
        with clients_lock:
            clients.pop(client_socket, None)
        
        client_socket.close()
        
        if username:
            broadcast(f"[{timestamp()}] [SERVER] {username} has left.", room)
            print(f"[{timestamp()}] [DISCONNECTED] {username}")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    
    print(f"\nServer listening on {HOST}:{PORT}\n")
    
    try:
        while True:
            client_socket, client_address = server.accept()
            
            thread = threading.Thread(
                target = client_handler,
                args = (client_socket, client_address),
                daemon = True
            )
            
            thread.start()
    
    except KeyboardInterrupt:
        print("\nShutting down server....")
        
        with clients_lock:
            current_clients = list(clients)
            
        for client in current_clients:
            client.close()
        
        print("\nServer stopped.")
        server.close()

if __name__ == "__main__":
    main()