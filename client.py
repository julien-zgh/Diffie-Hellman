import socket
import random
from colorama import Fore, init
from cryptography.fernet import Fernet
import base64

# Function to decrypt message
def decrypt_msg(shared_secret, msg):
    # Ensure shared_secret is a byte string
    shared_secret_bytes = str(shared_secret).encode('utf-8')

    # Make sure the byte string is 32 bytes long (pad if necessary)
    if len(shared_secret_bytes) < 32:
        shared_secret_bytes = shared_secret_bytes.ljust(32, b'\0')  # Pad with null bytes
    elif len(shared_secret_bytes) > 32:
        shared_secret_bytes = shared_secret_bytes[:32]  # Truncate to 32 bytes

    # Encode the key into URL-safe base64
    key_bytes = base64.urlsafe_b64encode(shared_secret_bytes)

    # Initialize the Fernet cipher with the key
    cipher = Fernet(key_bytes)
    
    # Decrypt the message
    decrypted_msg = cipher.decrypt(msg).decode()  # Expecting byte data
    return decrypted_msg

init(autoreset=True)  # Auto-reset colors after each print

# Connect to server
'''
AF_INET => IPV4
SOCK_STREAM => connection oriented => TCP
'''
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))

# Receive public parameters (p, g)
p, g = map(int, client.recv(1024).decode().split(","))
'''
The map() function applies the int function to each element in 
the list returned by .split(","), converting each string into 
an integer.
'''
print(Fore.CYAN + f"Received public parameters p={p}, g={g}")

# client generates private and public keys
client_private = random.randint(2, p-2)
client_public = (g ** client_private) % p

# Receive server's public key
server_public = int(client.recv(1024).decode())
print(Fore.YELLOW + f"Received Server's Public Key: {server_public}")

# Send client's public key
client.send(str(client_public).encode())

# Compute shared secret
shared_secret = (server_public ** client_private) % p
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

# Keep receiving messages until 'end' is received
while True:
    encrypted_msg = client.recv(1024)  # Receive the encrypted message
    print(Fore.LIGHTBLUE_EX + f"Received Message from server Before Decryption: {encrypted_msg}")
    message = decrypt_msg(shared_secret, encrypted_msg)
    print(Fore.LIGHTRED_EX + f"Received Message from server After Decryption: {message}")
    
    if message.lower() == 'end':
        print(Fore.YELLOW + "Ending connection.")
        break

print(Fore.RED + "Connection closed.")
client.close()
