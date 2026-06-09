import socket
from concurrent.futures import ThreadPoolExecutor

target = input("Enter hostname or target IP: ")
print(f"Scanning {target}....")

def scan(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    
    result = sock.connect_ex((target, port))
    
    if result == 0:
        return port
    
    sock.close()
    return None

open_ports = []

with ThreadPoolExecutor(max_workers=100) as executor:
    results = executor.map(scan, range(1, 1025))
    
    for port in results:
        if port is not None:
            open_ports.append(port)
            
for port in sorted(open_ports):
    print(f"Port {port} is OPEN")
    
print("Scan complete.")