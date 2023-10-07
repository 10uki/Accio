import socket
import sys
import threading
import signal
import os

socket.setdefaulttimeout(10)

HOST = '0.0.0.0'
file_dir = ""

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.exit(0)

# Set signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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
        except socket.error as e:
            # Handle binding errors and exit with an error message
            sys.stderr.write(f"ERROR: Connection failed.\n")
            sys.exit(1)
        # Return the established socket
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

def handle_client(conn, connection_number):
    try:
        conn.send(b'accio\r\n')

        # Receive and save data into a file
        data = conn.recv(1024)

        file_path = os.path.join(file_dir, f"{connection_number}.file")

        with open(file_path, "wb") as file:
            while data:
                file.write(data)
                data = conn.recv(1024)

    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

def main():
    global file_dir

    if len(sys.argv) != 3:
        sys.stderr.write("ERROR: Usage - python3 server.py <PORT> <FILE-DIR>\n")
        sys.exit(1)

    PORT = sys.argv[1]
    file_dir = sys.argv[2]

    try:
        PORT = int(PORT)
        if not 1 <= PORT <= 65535:
            raise ValueError
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    # Create the file directory if it does not exist
    os.makedirs(file_dir, exist_ok=True)

    with establish_connection(HOST, PORT) as s:
        connection_number = 0
        while True:
            try:
                conn, addr = s.accept()
                connection_number += 1
                client_thread = threading.Thread(target=handle_client, args=(conn, connection_number))
                client_thread.start()
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
