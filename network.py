import socket
import uuid


FORMAT = "utf-8"
MAX_BUFFER_LENGTH = 2048


class Connection:
    def __init__(self, sock, addr):
        self._uuid = uuid.uuid4()
        self._socket = sock
        self._address = addr
    
    def close(self):
        self._socket.close()

    def read(self):
        try:
            data = self._socket.recv(MAX_BUFFER_LENGTH).decode(FORMAT)
            if not data:
                raise ReadError()
            return data
        except socket.error as e:
            raise ReadError()

    def write(self, data):
        try:
            self._socket.send(data.encode(FORMAT))
        except socket.error as e:
            raise WriteError()
            
    def setblocking(self, blocking):
        self._socket.setblocking(blocking)
    
    def __str__(self):
        return str(self._socket.getpeername())

    def fileno(self):
        return self._socket.fileno()

    def __hash__(self):
        return hash(self._uuid)


class TCPClient(Connection):
    def __init__(self, host, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        super().__init__(self._socket, (host, port))


class TCPServer:
    MAX_CONNECTION_WAITING = 1000

    def __init__(self, host, port) -> None:
        self._host = host
        self._port = port
        self._prepare()

    def _prepare(self):
        self._socket = socket.socket()
        self._socket.bind((self._host, self._port))
        self._socket.listen(self.MAX_CONNECTION_WAITING)
        self._socket.setblocking(False)
    
    def accept(self):
        return Connection(*self._socket.accept())
    
    def fileno(self):
        return self._socket.fileno()

    def close(self):
        self._socket.close()


class ConnectionException(Exception):
    pass


class ReadError(ConnectionException):
    pass


class WriteError(ConnectionException):
    pass
