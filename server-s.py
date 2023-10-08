import socket
import signal
import sys
import threading

socket.setdefaulttimeout(10)

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.exit(0)

# Set signal handlers
for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
    signal.signal(sig, signal_handler)


def handle_client(conn, addr):
    try:
        total_bytes_received = 0
        conn.send(b'accio\r\n')

        while True:
            data = conn.recv(1024)
            if not data:
                break
            sent = conn.send(data)  # Send the received data back to the client
            if sent == 0:
                sys.stderr.write("ERROR: Server disconnected.\n")
                raise RuntimeError
            total_bytes_received += len(data)

            print(total_bytes_received)

    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Usage - python3 server-s.py <PORT>\n")
        sys.exit(1)

    PORT = sys.argv[1]

    try:
        # A valid range for TCP port numbers (1-65535).
        PORT = int(PORT)
        if not 1 <= PORT <= 65535:
            sys.stderr.write("ERROR: Invalid port number.\n")
            sys.exit(1)
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    try:
        # Create a socket object using IPv4 and TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10)
        try:
            # Bind the socket to the provided host (0.0.0.0) and port
            s.bind((HOST, PORT))
            # Listen for incoming connections with a backlog of 10
            s.listen(10)
        except socket.error:
            sys.stderr.write("ERROR: Connection failed.\n")
            raise
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        raise

    try:
        conn, addr = s.accept()
        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")


if __name__ == "__main__":
    main()