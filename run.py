import os
import platform
import subprocess
import sys

def start_server():
    """Starts the chat server (server.py) in a new terminal window."""
    print("[INFO] Starting the local chat server...")
    try:
        # Use Popen to run server.py in a new process console.
        if platform.system() == "Windows":
            subprocess.Popen([sys.executable, "server.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([sys.executable, "server.py"])
        print("[INFO] Server process has been started in a new window.")
        print("[INFO] Clients on the same local network can now connect.")
    except Exception as e:
        print(f"[ERROR] Failed to start server.py: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    start_server()
