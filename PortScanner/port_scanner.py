import sys
import socket
import time
from concurrent.futures import ThreadPoolExecutor

TIMEOUT = 0.3
MAX_THREADS = 200
BUFFER_SIZE = 1024

def main():
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

    if p1 > p2:
        print("Starting port must be less than or equal to ending port.")
        sys.exit(1)

    try:
        target_ip = socket.gethostbyname(target)
        
    except socket.gaierror:
        print("Could not resolve hostname.")
        sys.exit(1)

    start_time = time.perf_counter()

    if target != target_ip: 
        print(f"\nScanning {target} ({target_ip})\n")
    else:
        print(f"\nScanning {target}\n")
    
    def scan(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(TIMEOUT)
            
            port_start = time.perf_counter()
            result = sock.connect_ex((target_ip, port))
            port_end = time.perf_counter()
            
            response_time = (port_end - port_start) * 1000 #ms conversion
            
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                    
                except OSError:
                    service = "Unknown"
                    
                try:
                    banner = sock.recv(BUFFER_SIZE).decode(errors="ignore").strip()
                    if not banner:
                        banner = "No Banner"
                        
                except (socket.timeout, OSError):
                    banner = "No Banner"
                    
                return {
                    "port": port,
                    "service": service,
                    "banner": banner,
                    "response_time": response_time
                }
                    
        return None

    open_ports = []

    ports_scanned = p2 - p1 + 1
    status = "Completed"

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = executor.map(scan, range(p1, p2+1))
        
        completed = 0
        
        try:
            for result in results:
                completed += 1
                
                if result is not None:
                    open_ports.append(result)
                    
                if completed % 1000 == 0:
                    print(f"Scanned {completed}/{ports_scanned} ports", flush=True)
        except KeyboardInterrupt:
            print("\nScan interrupted")
            ports_scanned = completed
            status = "Interrupted"
                    
    end_time = time.perf_counter()
    time_taken = end_time - start_time

    print("=======================================")
    print("Scan Results")
    print("=======================================\n")

    if not open_ports:
        print("No open ports found")
    else:
        for info in sorted(open_ports, key=lambda x: x["port"]):
            print(
                f'{info["port"]}/tcp\t'
                f'{info["service"]:<8}\t'
                f'{info["response_time"]:>5.2f} ms\t'
                f'{info["banner"]}'
            )
    print("\nTarget: ", target)
    if target != target_ip:
        print("Resolved IP: ", target_ip)
    print("Ports Scanned: ", ports_scanned)
    print("Open Ports: ", len(open_ports))
    print(f"Time taken: {time_taken:.2f} seconds")
    print("Status: ", status)

try:
    main()
except KeyboardInterrupt:
    sys.exit(0)