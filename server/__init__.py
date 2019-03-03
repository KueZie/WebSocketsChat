from tinydb import TinyDB, Query 
import socket
import selectors
import types

class Server:

    _MAX_BUF = 1024

    def __init__(self, host, port):
        print("[SERVER] Initializing server socket.")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket.
        self.server_socket.bind( (host, port) )
        self.server_socket.listen()

        print(f"[SERVER] Listening on {host}:{port}")
        self.server_socket.setblocking(False)

        self._db = TinyDB("./database.json")
        self._query = Query()

        self.selector = selectors.DefaultSelector() # Setup selector

        _buffer = b"" # Read in buffer

        try:
            print("[SERVER] Registering")
            self.selector.register(self.server_socket, selectors.EVENT_READ, data=None)
        except Exception as e:
            print(f"[FATAL] Failed to register server: {e}")

        self.start()

    def accept_client(self):
        connection, address = self.server_socket.accept()
        print(f"[SERVER] Accepted connection from {address}")
        connection.setblocking(False) # Make sure connection socket does not "hang"
        data = types.SimpleNamespace(address=address, in_buffer=b"", out_buffer=b"") # Holds initial buffer and address data

        self.selector.register(connection, selectors.EVENT_READ | selectors.EVENT_WRITE, data) # Register connection that can be read and written to

        # table = self._db.insert({"uuid": 1}) # INCOMPLETE

    def handle_connection(self, key, bitmask):
        sock = key.fileobj
        data = key.data

        if bitmask & selectors.EVENT_READ:
            self._buffer = sock.recv(self._MAX_BUF)
            bytes_recieved = len(self._buffer)
            if bytes_recieved != 0:
                print(f"Recieved \"{self._buffer}\" from {sock.getsockname()}")
                data.out_buffer += self._buffer
            else:
                print(f"[SERVER] Closing connection to {data.address}.")
                self.selector.unregister(sock)
                sock.close()
        if bitmask & selectors.EVENT_WRITE:
            if data.out_buffer:
                print(f"Sending {repr(data.out_buffer)} to {data.address}")
                bytes_sent = sock.send(data.out_buffer)
                data.out_buffer = data.out_buffer[bytes_sent:]

    def start(self):
        try:
            while True:
                events = self.selector.select(timeout=1)
                for key, bitmask in events:
                    if key.data == None:
                        self.accept_client()
                    else:
                        self.handle_connection(key, bitmask)

        except KeyboardInterrupt:
            pass
        finally:
            self.selector.close()


    