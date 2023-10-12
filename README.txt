A simple client-server application that transfers a file over a TCP connection. This project is split into 3 parts:
1. Client
Accio client is a relatively simple application that connects to a server and sends a binary file utilizing accio\r\n sequence.
2. Simple Server
The simplified Accio server is another relatively simple application that waits for clients to connect, accepts a connection, 
sends the accio\r\n command, afterwards receives confirmation, sends the accio\r\n command again, receives the second confirmation, 
and then receives binary file that client sends, counts the number of bytes received, and prints it out as a single number 
(number of bytes received not including the header size).
3. Server
The Accio server is an extension of the simplified server that processes multiple simultaneous connections in parallel
saves the received data into the specified folder. Note that filenames should strictly follow what defined in the spec: 
1.file, 2.file, etc.