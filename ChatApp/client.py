import socket
import threading

HOST = "127.0.0.1"
PORT = 5555

username = input("Enter username: ")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST, PORT))
client.send(username.encode())

response = client.recv(1024).decode()

if response != "OK":
    print(response)
    client.close()
    exit()

def receive_msg():
    while True:
        try:
            message = client.recv(1024).decode()

            if not message:
                break
            
            print(f"\n{message}")
            
        except:
            break

threading.Thread(target = receive_msg, daemon = True).start()

while True:
    message = input(f"{username}> ")
    
    if message.lower() == "quit":
        break
    
    client.send(message.encode())

client.close()