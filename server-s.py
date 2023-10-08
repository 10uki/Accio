import socket
import signal
import sys
import threading

# Constants
HOST = "0.0.0.0"

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.exit(0)

# Set signal handlers
def setup_signal_handlers():
    for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
        signal.signal(sig, signal_handler)

def handle_client(conn, addr):
    try:
        total_bytes_received = 0
        conn.send(b'accio\r\n')

        with conn:
            while True:
                data = conn.recv(socket.SOL_SOCKET)
                if not data:
                    break
                total_bytes_received += len(data)

                sent = 0
                while sent < len(data):
                    sent += conn.send(data[sent:])

                print(f"Received {total_bytes_received} bytes")  # Print bytes received

    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")


def establish_connection(PORT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(10)
        s.bind((HOST, PORT))
        s.listen(10)
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        raise

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Usage - python3 server-s.py <PORT>\n")
        sys.exit(1)

    PORT = sys.argv[1]

    try:
        PORT = int(PORT)
        if not 1 <= PORT <= 65535:
            sys.stderr.write("ERROR: Invalid port number.\n")
            sys.exit(1)
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    setup_signal_handlers()

    try:
        s = establish_connection(PORT)
        conn, addr = s.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
