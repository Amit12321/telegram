from abc import ABCMeta, abstractmethod
import collections

from common import Message, IChatServer

class ChatCommand(metaclass=ABCMeta):
    def __init__(self, server: IChatServer, command, **kwargs) -> None:
        self._server = server
        self._command = command
        self._user = kwargs["user"]
        self._params = kwargs["params"]

    @abstractmethod
    def execute(self):
        pass


class HelpCommand(ChatCommand):
    def execute(self):
        help_message = """You can send messages to all the other users connected.
        Messages that start with @ are treated as special commands. The possible commands are:
        @help - list all commands.
        @private [user] [msg] - send a private message to user with the specified text.
        @name [new_name] - Changes your name to new_name, if not taken already.
        @online - shows a list of all the users currently online.
        @quit - quits the chat.
        """
        self._server._add_server_message(help_message, self._user)


class NameCommand(ChatCommand):
    def execute(self):
        if len(self._params) < 2:
            self._server._add_server_message(f"Wrong syntax! the syntax of the name command is: @name [new_name]", self._user)
            return
        new_name = self._params[1]
        if not new_name.upper() == "SERVER" and self._server._clients.change_name(self._user, new_name):
            self._server._add_server_message(f"The user {self._user} changed his name to {new_name}")
        else:
            self._server._add_server_message(f"The name {new_name} is already taken", self._user)


class OnlineCommand(ChatCommand):
    def execute(self):
        self._server._add_server_message(self._server._clients.get_all_names(), self._user)


class MessageCommand(ChatCommand):
    def execute(self):
        text = " ".join(self._params)
        self._server._add_message(Message(self._user, text))


class PrivateCommand(ChatCommand):
    def execute(self):
        if len(self._params) < 3:
            self._server._add_server_message(f"Wrong syntax! the syntax of the private command is: @private [user] [message]", self._user)
            return
        reciever_name = self._params[1]
        text = " ".join(self._params[2:])
        if not self._server._clients.does_name_exist(reciever_name):
            self._server._add_server_message(f"The user {reciever_name} doesn't exist.", self._user)
            return
        self._server._add_message(Message(self._user, text), reciever_name)


class QuitCommand(ChatCommand):
    def execute(self):
        self._server._remove_connection(self._server._clients.get_connection_for_name(self._user))
        self._server._add_server_message(f"The user {self._user} has quit the chat")


class InvalidCommand(ChatCommand):
    def execute(self):
        self._server._add_server_message(f"The command {self._command} doesn't exist. see @help for list of commands", self._user)


class CommandFactory:
    def __init__(self) -> None:
        self._commands = {}

    def register_command(self, command, command_class):
        self._commands[command] = command_class

    def get_command(self, server, command_name, **kwargs):
        command = self._commands.get(command_name)
        if not command:
            command = InvalidCommand
        return command(server, command_name, **kwargs)


factory = CommandFactory()
factory.register_command("help", HelpCommand)
factory.register_command("message", MessageCommand)
factory.register_command("online", OnlineCommand)
factory.register_command("quit", QuitCommand)
factory.register_command("private", PrivateCommand)
factory.register_command("name", NameCommand)
factory.register_command("invalid", InvalidCommand)
