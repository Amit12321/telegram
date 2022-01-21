from abc import ABCMeta, abstractmethod
import json

from common import COMMAND_TYPES

class Serializer(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def serialize(self, data):
        pass

class JSONSerializer(Serializer):
    COMMAND_SIGN = "@"

    def serialize(self, data: str):
        params = data.split(" ")
        if params[0].startswith(self.COMMAND_SIGN):
            command = params[0][1:]
            if command not in COMMAND_TYPES:
                command = "invalid"
        else:
            command = "message"

        return json.dumps({'command': command, 'params': params}, ensure_ascii=False)
