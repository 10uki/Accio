import socket
import signal
import sys
import threading

# Set default timeout to ten seconds.
socket.setdefaulttimeout(10)

# Set as '0.0.0.0' as per instructions.
HOST = "0.0.0.0"

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM).
def signal_handler(signum, frame):
    sys.exit(0)

# Set signal handlers.
for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
    signal.signal(sig, signal_handler)

def establish_connection(PORT):
    try:
        # Create a socket object using IPv4 and TCP protocol.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10)
        try:
            # Bind the socket to the provided host and port.
            s.bind((HOST, PORT))
            # Listen for incoming connections with a backlog of 10.
            s.listen(10)
        except socket.error:
            sys.stderr.write(f"ERROR: Connection failed.\n")
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


def handle_client(conn, addr):
    try:
        # Send the first accio command to the client.
        conn.send(b'accio\r\n')

        # Receive and validate the first confirmation.
        receive_confirmation(conn, b'confirm-accio\r\n')

        # Send the second accio command to the client.
        conn.send(b'accio\r\n')

        # Receive and validate the second confirmation.
        receive_confirmation(conn, b'confirm-accio-again\r\n\r\n')

        # Set bytes_received variable equal to zero.
        bytes_received = 0

        while True:
            # Receive data chunks of 1024 bytes of data from the socket otherwise exit loop.
            chunk = conn.recv(1024)
            if not chunk:
                break
            # Set bytes_received to length of received chunk.
            bytes_received = len(chunk)
        # Print bytes_received.
        print(bytes_received)
    # Handle a socket timeout exception and any other exceptions.
    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}.\n")
    # Finally, close connection.
    finally:
        conn.close()

def main():
    # Checks if the script is provided with the correct number of command-line
    # arguments. If not, display ValueError code and exits.
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Usage - python3 server-s.py <PORT>\n")
        sys.exit(1)

    # Extracts the port number from the command-line arguments.
    PORT = sys.argv[1]

    try:
        # Validate value of port is a valid integer between 1 and 65535.
        # If not, display ValueError code and exits.
        PORT = int(PORT)
        if not 1 <= PORT <= 65535:
            raise ValueError
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    with establish_connection(PORT) as s:
        # Continuously accept incoming client connections.
        while True:
            try:
                # Accept a new client connection and retrieve the client's address.
                conn, addr = s.accept()
                # Start a new thread to handle the client.
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.start()
            # Handle a socket timeout exception and any other exceptions.
            except socket.timeout:
                sys.stderr.write("ERROR: Connection Timeout.\n")
            except Exception as e:
                sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
