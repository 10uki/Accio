import socket
import signal
import sys
import time

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)
NOT_STOPPED = True

def handler(signum, frame):
    global NOT_STOPPED
    NOT_STOPPED = False
    sys.exit()

def main():
    global NOT_STOPPED
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

    # signal.signal(signal.SIGQUIT, handler)
    # signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    # TODO: CHANGE TIMEOUT TO 45
    socket.setdefaulttimeout(10)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, server_port))
        s.listen(10)
        try:
            conn, addr = s.accept()
            print(f"Connection from {addr} has been established.")
            conn.send(b'accio\r\n')
            with conn:
                total_bytes_received = 0

                while NOT_STOPPED:
                    data = conn.recv(1024)  # Receive data in chunks
                    while data:
                        total_bytes_received += len(data)

                    if total_bytes_received > 0:
                        print("Bytes Received:", total_bytes_received)

        except socket.timeout:
            sys.stderr.write("ERROR: Connection Timeout\n")

    s.close()
    sys.exit()

if __name__ == "__main__":
    main()