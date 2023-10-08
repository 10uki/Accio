import socket
import signal
import sys
import threading
import random
import time

socket.setdefaulttimeout(10)

# Constants
HOST = "0.0.0.0"
ERROR_PROBABILITY = 0.1
DELAY_TIME = 1

# Create a global lock
file_lock = threading.Lock()

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.exit(0)

# Set signal handlers
for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
    signal.signal(sig, signal_handler)

def establish_connection(host, port):
    try:
        # Create a socket object using IPv4 and TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10)
        try:
            # Bind the socket to the provided host and port
            s.bind((host, port))
            # Listen for incoming connections with a backlog of 10
            s.listen(10)
        except socket.error:
            sys.stderr.write(f"ERROR: Connection failed.\n")
            sys.exit(1)
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

def handle_client(conn, addr):
    try:
        conn.send(b'accio\r\n')

        confirmation = conn.recv(1024)
        if confirmation != b'confirm-accio\r\n':
            raise RuntimeError("Error: Invalid confirmation.")

        conn.send(b'accio\r\n')

        expected_bytes = 1024
        received_bytes = 0

        while received_bytes < expected_bytes:
            try:
                # Set timeout to 10 seconds for receiving data.
                conn.settimeout(10)
                # Receive data.
                data = conn.recv(1024)
                if not data:
                    break
                # Simulate transmission error.
                if random.random() < ERROR_PROBABILITY:
                    continue
                # Simulate delay
                time.sleep(DELAY_TIME)
                # Update received bytes.
                received_bytes += len(data)
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
                break
            except socket.error as e:
                sys.stderr.write("ERROR: Transmission error: {}\n".format(e))
                break

        print(received_bytes)

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

    finally:
        conn.close()

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

    with establish_connection(HOST, PORT) as s:
        while True:
            try:
                conn, addr = s.accept()
                # Start a new thread to handle the client.
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
