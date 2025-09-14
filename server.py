import socket
import random
from colorama import Fore, init
from cryptography.fernet import Fernet
import base64

# Function to encrypt message
def encrypt_msg(shared_secret, msg):
    # Ensure shared_secret is a byte string
    shared_secret_bytes = str(shared_secret).encode('utf-8')

    # Make sure the byte string is 32 bytes long (pad if necessary)
    if len(shared_secret_bytes) < 32:
        shared_secret_bytes = shared_secret_bytes.ljust(32, b'\0')  # Pad with null bytes
    elif len(shared_secret_bytes) > 32:
        shared_secret_bytes = shared_secret_bytes[:32]  # Truncate to 32 bytes

    # Encode the key into URL-safe base64 => 32-byte key
    key_bytes = base64.urlsafe_b64encode(shared_secret_bytes)

    # Initialize the Fernet cipher with the key
    cipher = Fernet(key_bytes)
    
    # Encrypt the message
    encrypted_msg = cipher.encrypt(msg.encode())
    return encrypted_msg

init(autoreset=True)  # Auto-reset colors after each print

# Start server's server
'''
AF_INET => IPV4
SOCK_STREAM => connection oriented => TCP
'''
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5555))

server.listen(1) # accept only 1 connection before rejecting any additional connections
print(Fore.RED + "Waiting for a connection...")

conn, addr = server.accept()
'''
1. conn: A new socket object that is used to communicate with the client that has just connected. This socket object is used to send and receive data between the server and the connected client.
2. addr: A tuple containing the address of the client that has connected. This address is typically in the form (host, port), where:
host is the IP address of the client (e.g., '127.0.0.1' for localhost or an external IP address).
port is the port number that the client is using for the connection.
'''
print(Fore.GREEN + f" Connected to Host: {addr}")

# server generates public parameters (p, g) and sends them to client
p = random.randint(100, 500)  # Choose a random prime-like number
g = random.randint(2, p-1)  # Choose a base

print(Fore.CYAN + f"Public Params p={p}, g={g}")
conn.send(f"{p},{g}".encode())  # Send parameters to client

# server generates private and public keys
server_private = random.randint(2, p-2)
server_public = (g ** server_private) % p

# Send server's public key
conn.send(str(server_public).encode())

# Receive client's public key
client_public = int(conn.recv(1024).decode())
print(Fore.YELLOW + f"Received Hosts's Public Key: {client_public}")

# Compute shared secret
shared_secret = (client_public ** server_private) % p
print(Fore.MAGENTA + f"Shared Secret Computed: {shared_secret}")

string = r'''
██████╗ ██╗███████╗███████╗██╗███████╗                        
██╔══██╗██║██╔════╝██╔════╝██║██╔════╝                        
██║  ██║██║█████╗  █████╗  ██║█████╗                          
██║  ██║██║██╔══╝  ██╔══╝  ██║██╔══╝                          
██████╔╝██║██║     ██║     ██║███████╗                        
╚═════╝ ╚═╝╚═╝     ╚═╝     ╚═╝╚══════╝                        
                                                              
██╗  ██╗███████╗██╗     ██╗      ███╗   ███╗ █████╗ ███╗   ██╗
██║  ██║██╔════╝██║     ██║      ████╗ ████║██╔══██╗████╗  ██║
███████║█████╗  ██║     ██║█████╗██╔████╔██║███████║██╔██╗ ██║
██╔══██║██╔══╝  ██║     ██║╚════╝██║╚██╔╝██║██╔══██║██║╚██╗██║
██║  ██║███████╗███████╗███████╗ ██║ ╚═╝ ██║██║  ██║██║ ╚████║
╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
'''
print(Fore.GREEN + f'{string}')

# Keep sending messages until 'end' is received
while True:
    message = input(Fore.WHITE + "Enter a message to send to Client (type 'end' to stop): ")
    
    # Encrypt and send message
    encrypted_msg = encrypt_msg(shared_secret, message)
    conn.send(encrypted_msg)
    
    if message.lower() == 'end':
        print(Fore.YELLOW + "Ending connection...")
        break

print(Fore.RED + " Connection closed.")
conn.close()
server.close()
