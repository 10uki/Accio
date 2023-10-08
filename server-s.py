import socket
import signal
import sys
import threading

socket.setdefaulttimeout(10)

HOST = "0.0.0.0"

# Function to handle signals (SIGINT, SIGQUIT, SIGTERM)
def signal_handler(signum, frame):
    sys.exit(0)

# Set signal handlers
for sig in [signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
    signal.signal(sig, signal_handler)

def handle_client(conn, addr):
    try:
        total_bytes_received = 0
        conn.send(b'accio\r\n')

        while True:
            data = conn.recv(1024)
            if not data:
                break
            # Send data in smaller chunks
            bytes_sent = 0
            while bytes_sent < len(data):
                sent = conn.send(data[bytes_sent:])
                if sent == 0:
                    raise RuntimeError("Error: Connection broken.")
                bytes_sent += sent
            total_bytes_received += len(data)

        print(total_bytes_received)

    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
    finally:
        conn.close()

def establish_connection(PORT):
    try:
        # Create a socket object using IPv4 and TCP protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout for socket operations
        s.settimeout(10)
        s.bind((HOST, PORT))
        s.listen(10)
        return s
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        raise

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Usage - python3 server-s.py <PORT>\n")
        sys.exit(1)

    PORT = sys.argv[1]

    try:
        PORT = int(PORT)
        if not 1 <= PORT <= 65535:
            sys.stderr.write("ERROR: Invalid port number.\n")
            sys.exit(1)
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    try:
        s = establish_connection(PORT)
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
