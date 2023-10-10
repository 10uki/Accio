import socket
import sys
import threading
import signal
import os
import time

# Set default timeout to ten seconds.
socket.setdefaulttimeout(10)

# Set as '0.0.0.0' as per instructions.
HOST = '0.0.0.0'


# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.exit(0)


# Set signal handlers.
for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
    signal.signal(sig, signal_handler)


def establish_connection(PORT):
    try:
        # Create a socket object using IPv4 and TCP protocol.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations.
        s.settimeout(10)
        try:
            # Bind the socket to the provided host and port.
            s.bind((HOST, PORT))
            # Listen for incoming connections with a backlog of 10.
            s.listen(10)
        except socket.error:
            sys.stderr.write("ERROR: Connection failed.\n")
            sys.exit(1)
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}.\n")
        sys.exit(1)


# Function to validate expected confirmation.
def receive_confirmation(conn, expected_confirmation):
    confirmation = conn.recv(len(expected_confirmation))
    if confirmation != expected_confirmation:
        sys.stderr.write("ERROR: Invalid confirmation.\n")
        raise RuntimeError


def handle_client(conn, file_dir, file_number):
    try:
        # Sets the initial timestamp when the function is first called.
        data_time = time.time()

        # Send the first accio command to the client.
        conn.send(b'accio\r\n')

        # Receive and validate the first confirmation.
        receive_confirmation(conn, b'confirm-accio\r\n')

        # Send the second accio command to the client.
        conn.send(b'accio\r\n')

        # Receive and validate the second confirmation.
        receive_confirmation(conn, b'confirm-accio-again\r\n\r\n')

        # Initialize an empty buffer to store received data.
        data = b""
        # Reset data_time to track the time since the last data reception.
        data_time = time.time()
        while True:
            # Receive data chunks of 1024 bytes of data from the socket otherwise exit loop.
            chunk = conn.recv(1024)
            if not chunk:
                break
            # Append the received chunk to the data buffer.
            data += chunk

            # Reset the timeout timer whenever data is received.
            data_time = time.time()
    # Handle any other exceptions that may occur during data transfer.
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}.\n")
        data = b"ERROR"

    # Check if no data received for more than 10 seconds.
    if time.time() - data_time > 10:
        sys.stderr.write("ERROR: Connection Timeout.\n")
        data = b"ERROR"

    # Write and save the data to a file with a sequential name and close connection.
    file_path = os.path.join(file_dir, f"{file_number}.file")
    with open(file_path, 'wb') as f:
        f.write(data)
    # Finally, close connection.
    conn.close()


def main():
    # Checks if the script is provided with the correct number of command-line
    # arguments. If not, display ValueError code and exits.
    if len(sys.argv) != 3:
        sys.stderr.write("ERROR: Usage - python3 server.py <PORT> <FILE-DIR>\n")
        sys.exit(1)

    # Extracts the port and file directory from the command-line arguments.
    PORT = int(sys.argv[1])
    file_dir = sys.argv[2]

    # Validate value of port is a valid integer between 1 and 65535.
    # If not, display ValueError code and exits.
    if not 1 <= PORT <= 65535:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    # Create the file directory if it does not exist
    os.makedirs(file_dir, exist_ok=True)

    with establish_connection(PORT) as s:
        # Initialize a counter for the received files.
        file_number = 1
        # Continuously accept incoming client connections.
        while True:
            try:
                # Accept a new client connection and retrieve the client's address.
                conn, addr = s.accept()
                # Start a new thread to handle the client.
                client_thread = threading.Thread(target=handle_client, args=(conn, file_dir, file_number))
                client_thread.start()
                # Increment file number size.
                file_number += 1
            # Handle a socket timeout exception and any other exceptions.
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: {str(e)}.\n")


if __name__ == "__main__":
    main()
