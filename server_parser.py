import json
import command

from common import ParseError, Parser


class ServerParser(Parser):
    def __init__(self, server):
        self._server = server

    def parse(self, sender, raw_data):
        try:
            data = json.loads(raw_data)
            return command.factory.get_command(self._server, data["command"], params=data["params"], user=sender)
        except (json.JSONDecodeError, KeyError) as e:
            raise ParseError()
        