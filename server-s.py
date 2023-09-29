
import socket
import signal
import sys

socket.setdefaulttimeout(10)

HOST = "0.0.0.0" # Standard loopback interface address (localhost)
RUNNING = True

def handler(signum, frame):
    global RUNNING
    RUNNING = False
    sys.exit()

def handle_client(conn, addr):
    try:
        conn.send(b'accio\r\n')
        total_bytes_received = 0

        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(data)

            total_bytes_received += len(data)

        print(total_bytes_received)

    except socket.timeout:
        sys.stderr.write("ERROR: Connection Timeout.\n")

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

    finally:
        conn.close()

def main():
    global RUNNING
    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Usage - python3 server-s.py <PORT>\n")
        sys.exit(1)

    PORT = int(sys.argv[1])

    try:
        # A valid range for TCP port numbers (1-65535).
        PORT = int(PORT)
        if not 1 <= PORT <= 65535:
            raise ValueError
    except ValueError:
        sys.stderr.write("ERROR: Invalid port number.\n")
        sys.exit(1)

    # signal.signal(signal.SIGQUIT, handler)
    # signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
            s.listen(10)

            while RUNNING:
                try:
                    conn, addr = s.accept()
                    handle_client(conn, addr)
                except socket.timeout:
                    sys.stderr.write("ERROR: Connection Timeout.\n")
        except OSError as e:
            sys.stderr.write(f"ERROR: {str(e)}\n")

    s.close()
    sys.exit()

if __name__ == "__main__":
    main()