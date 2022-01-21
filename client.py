import argparse
import threading

from screen import Screen
from connections import TCPClient, ReadError, WriteError
from client_serializer import JSONSerializer


class ChatClient:
    def __init__(self, *args, **kwargs):
       self._host = kwargs["host"]
       self._port = int(kwargs["port"])
       self._running = True
       self._screen = Screen()
       self._serializer = JSONSerializer()
       self._prepare_client()

    def _prepare_client(self):
        self._client = TCPClient(self._host, self._port)
        self._screen.display_text("Enter nickname: ")
        while not (name := self._screen.read_text()):
            continue
        self._client.write(name)
        answer = self._client.read()
        if answer == "EXIST":
            self._screen.display_text("The nickname is already used by another user. Try again.")
            self._client.close()
            self._prepare_client()
        self._name = name

    def _get_new_message(self):
        while self._running:
            message = self._screen.read_text()
            if not message:
                continue
            try:
                self._client.write(self._serializer.serialize(message))
            except WriteError:
                self._running = False

    def _display_new_message(self):
        try:
            message = self._client.read() 
            self._screen.display_text(message)
        except ReadError:
            self._running = False

    def run(self):
        t1 = threading.Thread(target=self._get_new_message)
        t1.start()
        while self._running:
            self._display_new_message()
        self._screen.display_text("The connection to the chat has ended. Press Enter to quit...")
        t1.join()
        self._client.close() 
        

parser = argparse.ArgumentParser(description='Chat client arguments.')
parser.add_argument('-host', nargs='?', default='localhost')
parser.add_argument('-port', nargs='?', default=8080)
args = parser.parse_args()

chat = ChatClient(**vars(args))
chat.run()
