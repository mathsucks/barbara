from collections import OrderedDict

from dotenv import dotenv_values


class Reader:
    """Reads environment variables into an ordered dictionary"""
    def __init__(self, source):
        self.source = source

    def read(self) -> OrderedDict:
        try:
            return dotenv_values(self.source)
        except TypeError:
            return dotenv_values(self.source.name)
