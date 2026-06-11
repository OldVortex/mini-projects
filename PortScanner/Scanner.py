import sys
import socket
import time
from concurrent.futures import ThreadPoolExecutor

if len(sys.argv) == 4:
    target = sys.argv[1]
    p1 = int(sys.argv[2])
    p2 = int(sys.argv[3])
    
elif len(sys.argv) == 1:
    target = input("Enter hostname or target IP: ")
    p1 = int(input("Starting Port: "))
    p2 = int(input("Ending Port: "))

else:
    print("Usage:")
    print("python portscanner.py <target> <starting port> <ending port>")
    sys.exit(1)

if not (1 <= p1 <= 65535 and 1 <= p2 <= 65535):
    print("Ports must be between 1 and 65535.")
    sys.exit(1)

if p1 >= p2:
    print("Staring port must be less than ending port.")
    sys.exit(1)

try:
    target_ip = socket.gethostbyname(target)
    
except socket.gaierror:
    print("Could not resolve hostname.")
    exit()

start_time = time.perf_counter()

print(f"\nScanning {target} {target_ip}")

def scan(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5) #Do not go below 300ms, might miss open ports
    
    try:
        result = sock.connect_ex((target_ip, port))
        if result == 0:
            return port
        
    finally:
        sock.close()
    
    return None

open_ports = []
service_dict = {}

with ThreadPoolExecutor(max_workers=100) as executor:
    results = executor.map(scan, range(p1, p2+1))
    
    for port in results:
        if port is not None:
            open_ports.append(port)
            
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = "Unknown"
            
            service_dict[port] = service
            
end_time = time.perf_counter()
time_taken = end_time - start_time
ports_scanned = p2 - p1 + 1

print("\n==============")
print("Scan Results")
print("==============\n")

if open_ports:
    for port in sorted(open_ports):
        service = service_dict[port]
        print(f"{port}/tcp\tOPEN\t{service}")
else:
    print("No open ports found.")

print("\nTarget: ", target)
print("Resolved IP: ", target_ip)
print("Ports Scanned: ", ports_scanned)
print("Open Ports: ", len(open_ports))
print(f"Time taken: {time_taken:.2f} seconds")