import socket
import uuid

from user import User

FORMAT = "utf-8"
MAX_BUFFER_LENGTH = 2048


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


class ChatClientPool:
    def __init__(self) -> None:
        self._connections = {}
    
    def does_name_exist(self, name):
        for _, user in self._connections.items():
            if user.name == name:
                return True
        return False

    def get_connection_for_name(self, name):
       for conn, user in self._connections.items():
            if user.name == name:
                return conn

    def get_name_for_connection(self, conn):
        if conn in self._connections:
            return self._connections[conn].name

    def change_name(self, old_name, new_name):
        if not self.does_name_exist(new_name):
            self._connections[self.get_connection_for_name(old_name)].name = new_name
            return True
        return False

    def get_all_names(self):
        return ", ".join([user.name for _, user in self._connections.items()])

    def add_connection(self, conn, name):
        self._connections[conn] = User(name)

    def remove_connection(self, conn):
        if conn in self._connections:
            del self._connections[conn]
    
    def add_message_to_one(self, reciever, message):
        self._connections[self.get_connection_for_name(reciever)].add_message(message)

    def add_message_to_all(self, message):
        for _, user in self._connections.items():
            if message.user != user.name:
                user.add_message(message)

    def get_next_message_for_connection(self, conn):
        return self._connections[conn].get_next_message()

    def __iter__(self):
        return iter(self._connections)



class ConnectionException(Exception):
    pass


class ReadError(ConnectionException):
    pass


class WriteError(ConnectionException):
    pass
