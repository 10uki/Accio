#!/usr/bin/env python3

import socket
import signal
import sys
import time

HOST = "0.0.0.0" # Standard loopback interface address (localhost)
not_stopped = True

def handler (signum,frame):
    not_stopped = False
   # time.sleep(15)
 #   s.close()
  #  sys.exit(0)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Usage - python3 server-s.py  <PORT> \n")
        sys.exit(1)

    server_port = sys.argv[1]

    try:
        # A valid range for TCP port numbers (1-65535).
        server_port = int(server_port)
        if not 1 <= server_port <= 65535:
            raise ValueError
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number\n")
        sys.exit(1)

    signal.signal(signal.SIGQUIT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)
    socket.setdefaulttimeout(10)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, server_port ))
        s.listen(10)

        while not_stopped:
            conn, addr = s.accept()
            with conn:
                try:
                    conn.send(b'accio\r\n')
                    data = conn.recv(1024)  # Receive data in chunks
                    total_bytes_received = len(data)

                    while data:
                        data = conn.recv(1024)
                        total_bytes_received += len(data)

                    print("Bytes Received:", total_bytes_received)
                except socket.timeout:
                    sys.stderr.write("ERROR: Connection Timeout\n")

    s.close()
    sys.exit()

if __name__ == "__main__":
    main()