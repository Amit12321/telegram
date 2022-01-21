from common import Singleton
import sys

class Screen(metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        self._stream = sys.stdin

    def read_text(self):
        return self._stream.readline().strip()

    def display_text(self, text):
        print(text)