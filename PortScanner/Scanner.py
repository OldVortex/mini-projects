import socket
import time
from concurrent.futures import ThreadPoolExecutor

target = input("Enter hostname or target IP: ")
p1 = int(input("Starting Port: "))
p2 = int(input("Ending Port: "))

start_time = time.perf_counter()

print(f"\nScanning {target}....")

def scan(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5) #Do not go below 300ms, might miss open ports
    
    try:
        result = sock.connect_ex((target, port))
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
print("Ports Scanned: ", ports_scanned)
print("Open Ports: ", len(open_ports))
print(f"Time taken: {time_taken:.2f} seconds")