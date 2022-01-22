import collections

class User:
    def __init__(self, name):
        self._name = name
        self._messages = collections.deque()
    
    def add_message(self, msg):
        self._messages.append(msg)
    
    def get_next_message(self):
        if len(self._messages) == 0:
            return None
        return self._messages.popleft()

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, new_name):
        self._name = new_name
    
    def __str__(self):
        return "[" + self._name + "]"


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