import socket
import sys

# Constants
MAX_CHUNKS = 10000

def receive_command(s, command):
    received_data = b""
    s.settimeout(10.0)
    try:
        while not received_data.endswith(command):
            chunk = s.recv(1)
            if not chunk:
                raise ConnectionError ("ERROR: Server disconnected.\n")
            received_data += chunk
    except socket.timeout:
        raise TimeoutError ("ERROR: Server disconnected for more than 10 seconds.\n")
    return received_data

def send_file(s, FILE):
    # Open the specified file for reading in binary mode
    try:
        with open(FILE, 'rb') as file:
            while True:
                chunk = file.read(MAX_CHUNKS)
                if not chunk:
                    break
                total_sent = 0
                while total_sent < len(chunk):
                    sent = s.send(chunk[total_sent:])
                    if sent == 0:
                        raise RuntimeError("ERROR: Socket connection broken.\n")
                    total_sent += sent
    except FileNotFoundError:
        sys.stderr.write("ERROR: File not found.\n")
        sys.exit(1)

def establish_connection(HOST, PORT):
    try:
        # Create a socket object using IPv4 and TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10.0)
        try:
            # Attempt to connect to the server using the provided host and port
            s.connect((HOST, PORT))
        except socket.error as e:
            # Handle connection errors and exit with an error message
            sys.stderr.write("ERROR: Connection failed.\n")
            sys.exit(1)
        # Return the established socket
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

def client():

    if len(sys.argv) != 4:
        sys.stderr.write("ERROR: Usage - python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>\n")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = sys.argv[2]
    FILE = sys.argv[3]

    try:
        PORT = int(PORT)
        if not (1 <= PORT<= 65535):
            sys.stderr.write("ERROR: Invalid port number.\n")
    except ValueError:
        sys.stderr.write("ERROR: Port number must be an integer.\n")
        sys.exit(1)
    s = establish_connection(HOST, PORT)

    receive_command(s, b'accio\r\n')
    s.send(b'confirm-accio\r\n')
    receive_command(s, b'accio\r\n')
    s.send(b'confirm-accio-again\r\n\r\n')
    send_file(s, FILE)
    print("File transfer successful")

    s.close()
    sys.exit(0)

if __name__ == '__main__':
    client()
