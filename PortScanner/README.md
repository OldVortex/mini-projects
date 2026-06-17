# Concurrent TCP Port Scanner

A multi-threaded TCP port scanner written in Python using sockets and `ThreadPoolExecutor`.

The scanner supports hostname resolution, service detection, banner grabbing, response-time measurement, progress tracking, and graceful interruption handling.

## Features

* Multi-threaded TCP port scanning
* Hostname and IP address support
* Service detection using well-known port mappings
* Banner grabbing for identifying running services
* Per-port response time measurement
* Command-line and interactive modes

---

## Requirements

* Python 3.8+
* Standard Python libraries only

No third-party packages are required.

---

## Usage

### Interactive Mode

Run the script without arguments:

```bash
python port_scanner.py
```

Example:

```text
Enter hostname or target IP: scanme.nmap.org
Starting Port: 1
Ending Port: 1024
```

### Command-Line Mode

```bash
python port_scanner.py <target> <start_port> <end_port>
```

Example:

```bash
python port_scanner.py scanme.nmap.org 1 1024
```

---

## Example Output

```text
Scanning scanme.nmap.org (45.33.32.156)

=======================================
Scan Results
=======================================

22/tcp  ssh             293.96 ms       SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13
53/tcp  domain            3.76 ms       No Banner
80/tcp  http            274.39 ms       No Banner

Target: scanme.nmap.org
Resolved IP: 45.33.32.156
Ports Scanned: 1024
Open Ports: 3
Time taken: 4.62 seconds
Status: Completed
```

---

## How It Works

1. Resolves the target hostname to an IP address.
2. Creates a pool of worker threads using `ThreadPoolExecutor`.
3. Attempts TCP connections to ports within the specified range.
4. Records successful connections as open ports.
5. Detects known services using Python's socket library.
6. Attempts banner grabbing from open ports.
7. Displays scan statistics and results.

---

## Error Handling

The scanner validates:

* Port ranges (1–65535)
* Start port <= end port
* Hostname resolution

It also handles:

* Invalid targets
* Connection timeouts
* Keyboard interruptions (Ctrl+C)

---

## Future Improvements

Potential enhancements include:

* UDP scanning
* Export results to CSV or JSON
* OS fingerprinting
* Configurable thread count
* Colorized terminal output
* Asyncio-based implementation
* IPv6 support

---

## Disclaimer

This project is intended for educational purposes and authorized security testing only. Do not scan systems without permission.
