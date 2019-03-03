from tinydb import TinyDB, Query 
import socket
import selectors

class Server():

    selector = selectors.DefaultSelector()
    client_sockets = []
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket.

    def __init__(self, host, port):
        print("[SERVER] Initializing server socket.")
        self.server_socket.bind( (host, port) )
        self.server_socket.listen()
        print(f"[SERVER] Listening on {host}:{port}")
        self.server_socket.setblocking(False)
        try:
            print("[SERVER] Registering")
            self.selector.register(self.server_socket, selectors.EVENT_READ, data=None)
        except Exception as e:
            print(f"[FATAL] Failed to register server: {e}")

    def accept(self):
        connection, address = self.server_socket.accept()
        print(f"[SERVER] Accepted connection from {address}")
        connection.setblocking(False) # Make sure connection socket does not "hang"


    