import json

from common import Serializer


class ClientSerializer(Serializer):
    COMMAND_SIGN = "@"

    def serialize(self, data: str):
        params = data.split(" ")
        if params[0].startswith(self.COMMAND_SIGN):
            command = params[0][1:]
        else:
            command = "message"

        return json.dumps({'command': command, 'params': params}, ensure_ascii=False)
