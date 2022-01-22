import selectors

from users_pool import ChatClientPool
from network import TCPServer, ReadError, WriteError
from server_parser import ServerParser, ParseError
from common import Message, IChatServer
from logger_factory import LoggerFactory

LOG_FILE = "telegram.log"
LOG_LEVEL = "INFO"

logger = LoggerFactory.get_logger(LOG_FILE, LOG_LEVEL)


class ChatServer(IChatServer):
    MAX_CONNECTIONS_WAITING = 1000
    SERVER_NAME = "SERVER"

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._clients = ChatClientPool()
        self._parser = ServerParser(self)
        self._prepare_server()

    def _prepare_server(self):
        self._selector = selectors.DefaultSelector()
        self._listener = TCPServer(self._host, self._port)
        self._selector.register(self._listener, selectors.EVENT_READ, self._accept)
        logger.info("Server is up and running...")

    def _accept(self, sock, mask):
        conn = self._listener.accept()
        self._selector.register(conn, selectors.EVENT_READ, self._add_connection)
        logger.info(f"New connection: {conn}.")

    def _read(self, conn, mask):
        self._read_message(conn)

    def _write(self, conn, mask):
        self._write_message(conn)

    def _read_write(self, conn, mask):
        if mask & selectors.EVENT_READ:
            self._read(conn, mask)
        if mask & selectors.EVENT_WRITE:
            self._write(conn, mask)

    def _add_connection(self, conn, mask):
        try:
            name = conn.read()
        except ReadError as e:
            logger.exception("A ReadError exception has occured.", exc_info=True)
            self._selector.unregister(conn)
            return
            
        if self._clients.does_name_exist(name) or name.upper() == self.SERVER_NAME:
            conn.write("EXIST")
            self._selector.unregister(conn)
            return

        conn.write("OK")

        self._clients.add_connection(conn, name)
        conn.setblocking(False)
        self._selector.modify(conn, selectors.EVENT_READ, self._read)
        self._add_server_message(f"{name} has joined the chat!")
        logger.info(f"The new connection {conn} chose the username {name}.")

    def _remove_connection(self, conn):
        logger.info(f"The connection with {conn} has ended.")
        self._selector.unregister(conn)
        conn.close()
        self._clients.remove_connection(conn)
        
    def _add_message(self, message, receiver_name = None):
        """
        If reciever_name is None, broadcasts the message to all users.
        otherwise, send it only to reciever, if exists.
        """
        if receiver_name is not None and self._clients.does_name_exist(receiver_name):
            self._clients.add_message_to_one(receiver_name, message)
            conn = self._clients.get_connection_for_name(receiver_name)
            # register every client connection for writing (broadcast recent messages)
            self._selector.modify(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, self._read_write)
            logger.info(f"Sending '{message.text}' from {message.user} to user {receiver_name}.")
        else:
            self._clients.add_message_to_all(message)
            logger.info(f"Sending '{message.text}' from {message.user} to all.")
            for conn in self._clients:
                self._selector.modify(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, self._read_write)

    def _add_server_message(self, text, username = None):
        self._add_message(Message(self.SERVER_NAME, text), username)

    def _read_message(self, conn):
        username = self._clients.get_name_for_connection(conn)
        try:
            data = conn.read()
            self._parser.parse(username, data).execute()
            logger.info(f"Recieved {data} from {conn}")
        except ReadError as e:
            logger.exception("A ReadError exception has occured.", exc_info=True)
            self._clients.remove_connection(conn)
        except ParseError as e:
            logger.exception("A ParseError exception has occured.", exc_info=True)
            self._add_server_message("An error has occured while parsing the command", username)

    def _write_message(self, conn):
        while msg := self._clients.get_next_message_for_connection(conn):
            try:
                conn.write(f"[{msg.user}] {msg.text}")
            except WriteError as e:
                logger.exception("A WriteError exception has occured.", exc_info=True)
                self._clients.remove_connection(conn)

        # if no more message to send, don't listen for write
        conn.setblocking(False) 
        self._selector.modify(conn, selectors.EVENT_READ, self._read)

    def shutdown(self):
        self._listener.close()
        logger.info("The server is shut down.")

    def run(self):
        while True:
            events = self._selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


server = ChatServer("127.0.0.1", 8080)
server.run()