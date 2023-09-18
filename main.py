import sys
import socket

# Constants
max_chunks = 10000
req_confirm = 2
timeout = 10


# command-line arguments
def validate_arguments(args):
    if len(args) != 4:
        sys.stderr.write("ERROR: Usage - python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>\n")
        sys.exit(1)

    server_host, server_port, filename = args[1], args[2], args[3]

    try:
        # A valid range for TCP port numbers (1-65535).
        server_port = int(server_port)
        if server_port < 1 or server_port > 65535:
            raise ValueError
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number\n")
        sys.exit(1)

    return server_host, server_port, filename


def receive_command(s, command):
    received_data = b""
    while not received_data.endswith(command):
        chunk = s.recv(1)
        if not chunk:
            raise RuntimeError("Server disconnected or did not send the expected command")
        received_data += chunk
        return received_data


def send_file(s, filename):
    # Open the specified file for reading in binary mode
    try:
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(max_chunks)
                if not chunk:
                    break
                total_sent = 0;
                while total_sent < len(chunk):
                    sent = s.send(chunk[total_sent:])
                    if sent == 0:
                        raise RuntimeError("Socket connection broken")
                    total_sent += sent
    except FileNotFoundError:
        sys.stderr.write("ERROR: File not found\n")
        sys.exit(1)


def establish_connection(server_host, server_port):
    try:
        # Create a socket object using IPv4 and TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(timeout)

        try:
            # Attempt to connect to the server using the provided host and port
            s.connect((server_host, server_port))
        except socket.error as e:
            # Handle connection errors and exit with an error message
            sys.stderr.write(f"ERROR: Connection failed - {e}\n")
            sys.exit(1)
        # Return the established socket
        return s

    except Exception as e:
        # Handle any other exceptions that might occur and exit with an error message
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)


def confirm_accio(s):
    confirmations = 0
    while confirmations < req_confirm:
        try:
            data = s.recv(1024).decode("utf-8")
            if data == "accio\r\n":
                s.send("confirm-accio\r\n".encode())
                confirmations += 1
        except socket.timeout:
            sys.stderr.write("ERROR: Timeout waiting for 'accio' command from server\n")
            s.close()
            sys.exit(1)


def client():
    # Extract the server host, server port, and file path from command-line arguments
    server_host, server_port, file_path = validate_arguments(sys.argv)
    # Establish a connection to the server
    s = establish_connection(server_host, server_port)
    # Confirm that the server is ready to receive data
    confirm_accio(s)
    # Send the file to the server
    send_file(s, file_path)
    # Close the socket connection and exit the program with a success code
    s.close()
    sys.exit(0)


if __name__ == "__main__":
    client()
