import socket
import threading
from datetime import datetime

# Connection Data
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 55555

# Lists for clients and their nicknames
clients = []
nicknames = []

# ANSI Color Codes
C_RESET = '\033[0m'
C_RED = '\033[91m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1)) # Connect to an arbitrary host to get local IP
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Fallback if no network is available
    finally:
        s.close()
    return IP

def get_timestamp():
    return datetime.now().strftime(f"{C_YELLOW}[%H:%M:%S]{C_RESET}")

# --- Functionality ---

# Broadcast messages to all connected clients
def broadcast(message, _client=None, system_message=False):
    timestamp = get_timestamp()
    if system_message:
        formatted_message = f"{timestamp} {C_YELLOW}SERVER:{C_RESET} {message.decode('ascii')}"
    else:
        # Assuming message is already formatted with nickname from client
        formatted_message = f"{timestamp} {message.decode('ascii')}"

    for client in clients:
        # Send to all clients except the sender
        if client != _client:
            try:
                client.send(formatted_message.encode('ascii'))
            except Exception as e:
                print(f"{C_RED}Error broadcasting to client: {e}{C_RESET}")
                remove_client(client)

# Handle individual client connections
def handle_client(client):
    while True:
        try:
            # Receive message from a client
            message = client.recv(1024)
            if message:
                broadcast(message, client)
            else:
                # If no message is received, the client has disconnected
                remove_client(client)
                break
        except Exception as e:
            # On error, assume client disconnected
            print(f"{C_RED}Error handling client: {e}{C_RESET}")
            remove_client(client)
            break

# Remove a client from the lists
def remove_client(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        nickname = nicknames[index]
        nicknames.remove(nickname)
        
        user_count = len(clients)
        system_leave_message = f'{nickname} left the chat! ({user_count} users online)'
        print(f"{get_timestamp()} {C_RED}{nickname} has disconnected. ({user_count} users online){C_RESET}")
        
        # Broadcast removal to remaining clients
        broadcast(system_leave_message.encode('ascii'), system_message=True)


# Main function to receive connections
def receive():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    local_ip = get_local_ip()
    print(f"{get_timestamp()} {C_GREEN}Server is listening on {HOST}:{PORT}{C_RESET}")
    print(f"{get_timestamp()} {C_GREEN}Local IP for clients on the same network: {local_ip}:{PORT}{C_RESET}")
    print(f"{get_timestamp()} {C_YELLOW}For connections from other states/networks, remember to use ngrok. Check ngrok instructions.{C_RESET}")

    while True:
        try:
            # Accept a new connection
            client, address = server.accept()
            print(f"{get_timestamp()} {C_GREEN}Connected with {str(address)}{C_RESET}")

            # Request and store nickname
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            
            # Check for duplicate nicknames (basic check)
            if nickname in nicknames:
                client.send(f"{C_RED}Nickname '{nickname}' already taken. Please choose another.{C_RESET}".encode('ascii'))
                client.close()
                print(f"{get_timestamp()} {C_YELLOW}Rejected connection for duplicate nickname: {nickname}{C_RESET}")
                continue # Continue to next connection

            nicknames.append(nickname)
            clients.append(client)

            # Announce the new client
            user_count = len(clients)
            print(f"{get_timestamp()} {C_BLUE}Nickname of the client from {address} is {nickname}. ({user_count} users online){C_RESET}")
            
            system_join_message = f"{nickname} joined the chat! ({user_count} users online)"
            broadcast(system_join_message.encode('ascii'), client, system_message=True)
            
            # Send initial welcome to the new client (with their own colors)
            client.send(f"{get_timestamp()} {C_GREEN}Connected to the server! Welcome, {C_CYAN}{nickname}{C_GREEN}! ({user_count} users online){C_RESET}".encode('ascii'))

            # Start a thread to handle the new client
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except Exception as e:
            print(f"{C_RED}Error accepting new connection: {e}{C_RESET}")
            # Consider a small delay before retrying or exiting on critical errors

# --- Main Execution ---
if __name__ == "__main__":
    receive()