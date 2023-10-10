import socket
import sys

# Set default timeout to ten seconds.
socket.setdefaulttimeout(10)

# Set max chunks to 10000.
MAX_CHUNKS = 10000


def receive_command(s, command):
    # Initialize an empty buffer to store received data.
    received_data = b""
    try:
        # Continue receiving data until the received_data ends with the specified command.
        while not received_data.endswith(command):
            # Receive one byte of data from the socket.
            chunk = s.recv(1)
            # If no data is received, raise a ConnectionError and print error message.
            if not chunk:
                sys.stderr.write("ERROR: Server disconnected.\n")
                raise ConnectionError
            # Append the received chunk to the data buffer.
            received_data += chunk
    except socket.timeout:
        # Handle a socket timeout exception raising a TimeoutError and print error message.
        sys.stderr.write("ERROR: Connection Timeout.\n")
        raise TimeoutError
    # Return the received data, which should now include the specified command.
    return received_data


def send_file(s, FILE):
    # Open the specified file for reading in binary mode
    try:
        with open(FILE, 'rb') as file:
            # While the size of the chunks is equal to the maximum permitted allowed
            # chunks send the length of the data, if the amount set is equal to zero
            # output RuntimeError code.
            while True:
                chunk = file.read(MAX_CHUNKS)
                if not chunk:
                    break
                total_sent = 0
                while total_sent < len(chunk):
                    sent = s.send(chunk[total_sent:])
                    if sent == 0:
                        sys.stderr.write("ERROR: Socket connection broken.\n")
                        raise RuntimeError
                    total_sent += sent
    # Otherwise, if the file is not found, FileNotFoundError.
    except FileNotFoundError:
        sys.stderr.write("ERROR: File not found.\n")
        sys.exit(1)


def establish_connection(HOST, PORT):
    try:
        # Create a socket object using IPv4 and TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10)
        try:
            # Attempt to connect to the server using the provided host and port
            s.connect((HOST, PORT))
        except socket.error:
            sys.stderr.write("ERROR: Connection failed.\n")
            raise
        # Return the established socket
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        raise


def client():
    # Checks if the script is provided with the correct number of command-line
    # arguments. If not, display ValueError code and exits.
    if len(sys.argv) != 4:
        sys.stderr.write("ERROR: Usage - python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>\n")
        sys.exit(1)

    # Extracts the host, port, and file name from the command-line arguments.
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    FILE = sys.argv[3]

    # Validate value of port is a valid integer between 1 and 65535.
    # If not, display ValueError code and exits.
    try:
        PORT = int(PORT)
        if not (1 <= PORT <= 65535):
            sys.stderr.write("ERROR: Invalid port number.\n")
            sys.exit(1)
    except ValueError:
        sys.stderr.write("ERROR: Port number must be an integer.\n")
        sys.exit(1)

    # Call establish_connection function with specified HOST and PORT.
    s = establish_connection(HOST, PORT)

    # Send and receive "accio" commands from the server using the receive_command function.
    try:
        receive_command(s, b'accio\r\n')
        s.send(b'confirm-accio\r\n')
        receive_command(s, b'accio\r\n')
        s.send(b'confirm-accio-again\r\n\r\n')

        # Send the file to the server.
        send_file(s, FILE)
        # Confirm file transfer successful.
        print("File transfer successful.")
    # In the case of network disconnection, display TimeoutError and exit.
    except TimeoutError:
        sys.stderr.write("ERROR: Connection Timeout.\n")
        sys.exit(1)
    # Handle any other exceptions that may occur during file transfer.
    except Exception as e:
        sys.stderr.write(f"ERROR: File transfer failed: {str(e)}.\n")
        sys.exit(1)

    s.close()
    sys.exit(0)


if __name__ == '__main__':
    client()
