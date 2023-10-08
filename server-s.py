import socket
import signal
import sys
import threading

socket.setdefaulttimeout(10)

HOST = "0.0.0.0"

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

        while True:  # Loop to handle multiple files within a single client connection
            total_bytes_received = 0

            file_name = f'received_file_from_{addr[0]}_{addr[1]}_{total_bytes_received}.bin'
            with file_lock:
                with open(file_name, 'wb') as file:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        file.write(data)
                        total_bytes_received += len(data)

            if total_bytes_received == 0:
                break

            print(total_bytes_received)

    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")

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
                # Start a new thread to handle the client
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
