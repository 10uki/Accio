import socket
import sys
import threading
import signal
import os
import time

socket.setdefaulttimeout(10)

HOST = '0.0.0.0'
file_dir = ""

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

def handle_client(conn, file_path):
    global file_dir
    global timeout_flag

    try:
        # Send first accio command to the client.
        conn.send(b'accio\r\n')

        # Receive confirmation from the client.
        confirmation = conn.recv(1024)
        if confirmation != b'confirm-accio\r\n':
            raise RuntimeError("Error: Invalid confirmation.")

        # Send second accio command to the client.
        conn.send(b'accio\r\n')

        # Receive and save the binary data sent by the client.
        with open(file_path, "wb") as file:
            data = conn.recv(1024)
            while data:
                # Update the last data time
                data_time = time.time()
                file.write(data)
                data = conn.recv(1024)

        # Set the timeout flag to False when data is received successfully
        timeout_flag = False

    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")
        # Write "ERROR" into the corresponding file and reset its content
        with open(file_path, "wb") as file:
            file.write(b"ERROR")

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}.\n")

    finally:
        conn.close()

def main():
    global file_dir
    global file_number

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
        while True:
            try:
                # Accept a new client connection.
                conn, addr = s.accept()

                # Generate a unique file path for the connection.
                file_path = os.path.join(file_dir, f"{file_number}.file")

                # Increment the file_number for the next connection
                file_number += 1

                # Create a new thread to handle the client with its connection and file path.
                client_thread = threading.Thread(target=handle_client, args=(conn, file_path))
                client_thread.start()

            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()