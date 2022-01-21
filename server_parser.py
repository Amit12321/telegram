from abc import ABCMeta, abstractmethod
import json
import command


class Parser(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def parse(self, data):
        pass

class ParseError(Exception):
    pass


class JSONParser(Parser):
    def __init__(self, server):
        self._server = server

    def parse(self, sender, raw_data):
        try:
            data = json.loads(raw_data)
            return command.factory.get_command(self._server, data["command"], params=data["params"], user=sender)
        except (json.JSONDecodeError, KeyError) as e:
            raise ParseError()
        