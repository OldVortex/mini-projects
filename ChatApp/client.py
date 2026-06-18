import socket

HOST = "127.0.0.1"
PORT = 5555

username = input("Enter username: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))
client.send(username.encode())

while True:
    message = input("Enter message: ")

    if message.lower() == "quit":
        break
    
    client.send(message.encode())

    reply = client.recv(1024).decode()
    print("Server:", reply)

client.close()