# Command-Line Chat Room

A simple command-line chat application built with Python's `socket` and `threading` libraries. It allows multiple users to connect to a central server and chat in real-time.

## Features

*   Real-time messaging
*   Multiple clients support
*   Colored text for better readability
*   Simple setup and usage

## Files

*   `server.py`: The chat server.
*   `client.py`: The chat client.
*   `run.py`: A script to easily start the server.

## How to Use

1.  **Start the server:**
    ```bash
    python run.py
    ```

2.  **Start the client:**
    Open a new terminal and run:
    ```bash
    python client.py
    ```
    You will be prompted to enter a server address (you can press Enter for localhost) and a nickname.

## Dependencies

*   Python 3
