#!/usr/bin/env python3

import socket
import signal
import sys

HOST = "0.0.0.0" # Standard loopback interface address (localhost)
not_stopped = True


def handler (signum,frame):
    not_stopped = False

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

 #  signal.signal(signal.SIGQUIT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)
    socket.setdefaulttimeout(10)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, server_port ))
        s.listen(10)

        try:
            conn, addr = s.accept()
            conn.send(b'accio\r\n')
            with conn:
                while not_stopped:
                    data = conn.recv(1024)  # Receive data in chunks
                    total_bytes_received = len(data)

                while data:
                    data = conn.recv(1024)
                    total_bytes_received += len(data)

                print(total_bytes_received)
        except socket.timeout:
            sys.stderr.write("ERROR: Connection Timeout\n")

    s.close()
    sys.exit()

if __name__ == "__main__":
    main()