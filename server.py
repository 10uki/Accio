import socket
import sys
import threading
import signal
import os

socket.setdefaulttimeout(10)

HOST = '0.0.0.0'

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.stderr.write("Received signal. Exiting gracefully...\n")
    sys.exit(0)

# Set signal handlers.
for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
    signal.signal(sig, signal_handler)

def establish_connection(host, port):
    try:
        # Create a socket object using IPv4 and TCP protocol.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10)
        try:
            # Bind the socket to the provided host and port.
            s.bind((host, port))
            # Listen for incoming connections with a backlog of 10.
            s.listen(10)
        except socket.error:
            sys.stderr.write(f"ERROR: Connection failed.\n")
            sys.exit(1)
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

def handle_client(conn, file_dir, file_number):
    try:
        # Send the first accio command to the client.
        conn.send(b'accio\r\n')

        # Receive confirmation from the client.
        confirmation = conn.recv(1024)
        if confirmation != b'confirm-accio\r\n':
            raise RuntimeError("Error: Invalid confirmation.")

        # Send the second accio command to the client.
        conn.send(b'accio\r\n')

        # Receive and save the binary data sent by the client.
        data = b""
        while True:
            chunk = conn.recv(1024)
            if not chunk:
                break
            data += chunk

    except socket.timeout:
        data = b"ERROR"

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}.\n")

    # Save the data to a file with a sequential name using the global lock.
    file_path = os.path.join(file_dir, f"{file_number}.file")
    with open(file_path, 'wb') as f:
        f.write(data)

    conn.close()

def main():
    if len(sys.argv) != 3:
        sys.stderr.write("ERROR: Usage - python3 server.py <PORT> <FILE-DIR>\n")
        sys.exit(1)

    PORT = int(sys.argv[1])
    file_dir = sys.argv[2]

    if not 1 <= PORT <= 65535:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    # Create the file directory if it does not exist
    os.makedirs(file_dir, exist_ok=True)

    with establish_connection(HOST, PORT) as s:
        file_number = 1
        client_threads = []  # Store client threads
        while True:
            try:
                conn, addr = s.accept()
                # Start a new thread to handle the client.
                client_thread = threading.Thread(target=handle_client, args=(conn, file_dir, file_number))
                client_thread.start()
                client_threads.append(client_thread)
                file_number += 1
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: {str(e)}\n")

            # Wait for all client threads to finish before exiting.
            for thread in client_threads:
                thread.join()

if __name__ == "__main__":
    main()
