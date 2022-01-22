import collections

from abc import ABCMeta, abstractmethod

Message = collections.namedtuple("Message", ["user", "text"])


class Serializer(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def serialize(self, data):
        pass


class Parser(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def parse(self, data):
        pass

class ParseError(Exception):
    pass


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls._instance = None
    
    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class IChatServer(metaclass=ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def _read(self):
        pass

    @abstractmethod
    def _write(self):
        pass

    @abstractmethod
    def _add_connection(self):
        pass
    
    @abstractmethod
    def _remove_connection(self):
        pass

    @abstractmethod
    def _add_message(self):
        pass

    @abstractmethod
    def _add_server_message(self):
        pass

    @abstractmethod
    def _read_message(self):
        pass

    @abstractmethod
    def _write_message(self):
        pass

    @abstractmethod
    def run(self):
        pass
