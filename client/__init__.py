import socket
import selectors
import sys
import types
import uuid

class Client:

    _selector = selectors.DefaultSelector()
    _server = ("127.0.0.1", 8080)
    _buffer = b""
    _MAX_BUF = 4096
    _id=uuid.uuid4()

    def __init__(self, username):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.setblocking(False)

        try:
            self._client_socket.connect_ex(self._server)
        except Exception as e:
            print(f"[FATAL] Failed to connect to server with address {self._server[0]}:{self._server[1]}. Error: {e}")

        self._username = username
        data = types.SimpleNamespace(out_buffer=b"", total_bytes_read=0)
        self._selector.register(self._client_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
        
        try:
            while True:
                events = self._selector.select(timeout=1)
                if events:
                    for key, bitmask in events:
                        self.handle_connection(key, bitmask)
        except KeyboardInterrupt:
            pass
        finally:
            self._selector.close()


    def handle_connection(self, key, bitmask):
        socket = key.fileobj
        data = key.data

        if bitmask & selectors.EVENT_READ:
            self._buffer = socket.recv(self._MAX_BUF)
            bytes_read = len(self._buffer)
            if len(self._buffer) != 0:
                print(f"[CLIENT] Recieved {self._buffer} from server : {socket}")
                data.total_bytes_read += bytes_read
            if bytes_read == 0:
                print(f"[CLIENT] Closing connection with server.")
                self._selector.unregister(socket)
                socket.close()
        if bitmask & selectors.EVENT_WRITE:
            if len(data.out_buffer) == 0:
                raw = input("-> ")
                msg = str(self._id) + "::::" + raw
                data.out_buffer = msg.encode()

            print(f"[CLIENT] Sending {msg} to server.")
            data_send = socket.send(data.out_buffer)
            data.out_buffer = data.out_buffer[data_send:]
client = Client("Hunter")