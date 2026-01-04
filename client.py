import socket
import threading
import sys

# ANSI Color Codes
C_RESET = '\033[0m'
C_RED = '\033[91m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_BLUE = '\033[94m'
C_CYAN = '\033[96m'

# --- Configuration ---
SERVER_HOST = input(f"{C_GREEN}Enter server address (IP or hostname, or press Enter for localhost): {C_RESET}")
if not SERVER_HOST:
    SERVER_HOST = '127.0.0.1'

try:
    SERVER_PORT_INPUT = input(f"{C_GREEN}Enter server port (or press Enter for default 55555): {C_RESET}")
    SERVER_PORT = int(SERVER_PORT_INPUT) if SERVER_PORT_INPUT else 55555
except ValueError:
    SERVER_PORT = 55555

NICKNAME = input(f"{C_GREEN}Choose your nickname: {C_RESET}")
if not NICKNAME:
    NICKNAME = "Guest" + str(id(SERVER_PORT)) # Simple unique ID if no nickname

# --- Client Setup ---
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((SERVER_HOST, SERVER_PORT))
except ConnectionRefusedError:
    print(f"{C_RED}Connection refused. Is the server running and accessible at {SERVER_HOST}:{SERVER_PORT}?{C_RESET}")
    sys.exit()
except socket.gaierror:
    print(f"{C_RED}Invalid server address or hostname: {SERVER_HOST}{C_RESET}")
    sys.exit()
except Exception as e:
    print(f"{C_RED}An unexpected error occurred during connection: {e}{C_RESET}")
    sys.exit()

stop_threads = False

# Listen for messages from the server
def receive_messages():
    global stop_threads
    while not stop_threads:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(NICKNAME.encode('ascii'))
            elif message.startswith(f"{C_RED}Nickname '{NICKNAME}' already taken"):
                print(f"\n{message}")
                print(f"{C_RED}Please restart the client and choose a different nickname.{C_RESET}")
                stop_threads = True
                client.close()
                break
            else:
                # Print message and re-draw the prompt
                sys.stdout.write(f"\r{message}\n{C_CYAN}{NICKNAME}{C_RESET}> ")
                sys.stdout.flush()
        except Exception as e:
            if not stop_threads: # Only print error if not intentionally closing
                print(f"\n{C_RED}An error occurred or connection lost: {e}{C_RESET}")
                print(f"{C_RED}Disconnected from server.{C_RESET}")
            stop_threads = True
            client.close()
            break

# Send messages to the server
def write_messages():
    global stop_threads
    while not stop_threads:
        try:
            # Use sys.stdin.readline for better handling with threads
            user_input = sys.stdin.readline().strip()
            
            if user_input.lower() == 'quit':
                stop_threads = True
                print(f"\n{C_YELLOW}Disconnecting from chat...{C_RESET}")
                client.send(f"{NICKNAME} has left the chat.".encode('ascii')) # Optional: notify server of disconnect
                client.close()
                break

            # Send message with nickname prefix
            message_to_send = f"{C_CYAN}{NICKNAME}{C_RESET}: {user_input}"
            client.send(message_to_send.encode('ascii'))
            
            # Re-draw the prompt after sending
            sys.stdout.write(f"{C_CYAN}{NICKNAME}{C_RESET}> ")
            sys.stdout.flush()

        except Exception as e:
            if not stop_threads:
                print(f"\n{C_RED}Failed to send message: {e}{C_RESET}")
            stop_threads = True
            client.close()
            break

# --- Main Execution ---
print(f"{C_GREEN}--- Welcome to the Chat Room, {C_CYAN}{NICKNAME}{C_GREEN}! ---")
print(f"{C_YELLOW}Type 'quit' to exit the chat.{C_RESET}")
print(f"{C_CYAN}{NICKNAME}{C_RESET}> ", end="", flush=True)

# Start a thread to receive messages
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True # Allows main program to exit even if thread is still running
receive_thread.start()

# Main thread handles writing messages
write_messages()

# Ensure all threads are stopped and client is closed on exit
if not stop_threads:
    client.close()