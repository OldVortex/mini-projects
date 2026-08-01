import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5555

COMMANDS = {
    "/users": "Show online users in the room",
    "/msg <user> <message>": "Send a private message to the user",
    "/room": "Show current room",
    "/rooms": "Show available chat rooms to join",
    "/join <room>": "Join the chat room",
    "/help": "Show list of commands"
}

rooms = {
    "general",
    "music"
}

history = {
    room: []
    for room in rooms
}

clients = {}

clients_lock = threading.Lock()
history_lock = threading.Lock()

def add_history(room, message):
    with history_lock:
        history[room].append(message)
        
        if len(history[room]) > 20:
            history[room].pop(0)

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
            client.send(f"[{timestamp()}] [PM] {sender}: {message}".encode())
            return True
    
    return False

def cmd_help(client_socket, username):
    help_text = "Available commands:\n"
    
    for command, description in COMMANDS.items():
        help_text += f"{command}: {description}\n"
    
    client_socket.send(help_text.encode())
    print(f"[{timestamp()}] [COMMAND] {username}: /help")
    
    return True
    
def cmd_users(client_socket, username):
    with clients_lock:
        curr_room = clients[client_socket]['room']
        current_clients = list(clients.values())
    
    online = []
    
    for info in current_clients:
        if info['room'] == curr_room:
            online.append(f"• {info['username']}")
    
    online = "\n".join(online)
    
    client_socket.send(f"Online users:\n{online}".encode())
    print(f"[{timestamp()}] [COMMAND] {username}: /users")
    
    return True
    
def cmd_rooms(client_socket, username):
    room_list = "\n".join(f"• {room}" for room in sorted(rooms))
    
    client_socket.send(f"Available rooms: \n{room_list}".encode())
    print(f"[{timestamp()}] [COMMAND] {username}: /rooms")
    
    return True
    
def cmd_room(client_socket, username):
    
def cmd_join(client_socket, username, parts):
    if len(parts) < 2:
        client_socket.send("Usage: /join <room>".encode())
        return True
    
    room = parts[1].lower()
    
    if room not in rooms:
        client_socket.send("Room does not exist.".encode())
        return True
    
    with clients_lock:
        prev_room = clients[client_socket]['room']
        
    if room == prev_room:
        client_socket.send("You are already in this room.".encode())
        return True
    
    broadcast(f"[SERVER] {username} has left '{room}'.", room, sender = client_socket)
    
    with clients_lock:
        clients[client_socket]['room'] = room
        
    broadcast(f"[SERVER] {username} has joined '{room}'.", room, sender = client_socket)
    client_socket.send(f"You have joined '{room}'.\n".encode())
    print(f"[{timestamp()}] [ROOM] {username}: {prev_room} -> {room}")
            
    return True

def cmd_msg(client_socket, username, parts):
    if len(parts) < 3:
        client_socket.send("Usage: /msg <user> <message>". encode())
        return True
    
    recipient = parts[1]
    private_msg = parts[2]
    
    print(f"[{timestamp()}] [PM] {username} -> {recipient}")
    
    success = send_private_msg(username, recipient, private_msg)
    if not success:
        client_socket.send(f"User '{recipient}' not found".encode())
    
    return True

def command_handler(client_socket, username, message):    
    if message == "/users":
        return cmd_users
    
    if message == "/help":
        return cmd_help(client_socket, username)
    
    if message == "/rooms":
        return cmd_rooms(client_socket, username)
    
    if message.startswith("/msg "):
        parts = message.split(" ", 2)
        return cmd_msg(client_socket, username, parts)
    
    if message.startswith("/join "):
        parts = message.split(maxsplit = 1)
        return cmd_join(client_socket, username, parts)
    
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
        
        with clients_lock:
            curr_room = clients[client_socket]['room']
        
        print(f"[{timestamp()}] [CONNECTED] {username} ({client_address[0]}:{client_address[1]})")
        
        broadcast(f"[{timestamp()}] [SERVER] {username} joined.", curr_room)
        
        with history_lock:
            messages = history[curr_room].copy()
        
        if messages:
            client_socket.send("\n------ Recent Messages -----\n".encode())
            
            for msg in messages:
                client_socket.send(f"{msg}\n".encode())
            
            client_socket.send("----------------------------\n".encode())
        
        while True:
            message = client_socket.recv(1024).decode()
            
            with clients_lock:
                curr_room = clients[client_socket]['room']
            
            if not message:
                break
            
            if command_handler(client_socket, username, message):
                continue
            
            formatted = f"[{timestamp()}] [MESSAGE] {username}: {message}"
            
            add_history(curr_room, formatted)
            print(formatted)
            broadcast(formatted, curr_room, sender = client_socket)
    
    except ConnectionResetError:
        pass
    
    finally:
        with clients_lock:
            info = clients.pop(client_socket, None)
        
        room = info['room'] if info else None
        
        client_socket.close()
        
        if username and room:
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