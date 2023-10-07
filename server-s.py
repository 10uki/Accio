import socket
import signal
import sys

socket.setdefaulttimeout(10)

HOST = "0.0.0.0"  # Standard loopback interface address (localhost)

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.exit(0)

# Set signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def establish_connection(HOST, PORT):
    try:
        # Create a socket object using IPv4 and TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10)
        try:
            # Bind the socket to the provided host and port
            s.bind((HOST, PORT))
            # Listen for incoming connections with a backlog of 10
            s.listen(10)
        except socket.error as e:
            sys.stderr.write(f"ERROR: Connection failed.\n")
            sys.exit(1)
        # Return the established socket
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

def handle_client(conn, addr):
    try:
        total_bytes_received = 0
        conn.send(b'accio\r\n')

        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
                total_bytes_received += len(data)
            print(total_bytes_received)

    except socket.timeout:
        sys.stderr.write(f"ERROR: Connection Timeout.\n")

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
            raise ValueError
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    try:
        s = establish_connection(HOST, PORT)

        while True:
            try:
                conn, addr = s.accept()
                handle_client(conn, addr)
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
