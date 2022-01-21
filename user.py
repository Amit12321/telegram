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