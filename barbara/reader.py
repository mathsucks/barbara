from collections import OrderedDict

import boto3
from dotenv import dotenv_values


class Reader:
    """Reads environment variables from file into an ordered dictionary"""
    def __init__(self, source):
        self.source = source

    def read(self) -> OrderedDict:
        try:
            return dotenv_values(self.source)
        except TypeError:
            return dotenv_values(self.source.name)


class SSMReader:
    """Reads environment variables from AWS SSM storage into an ordered dictionary"""
    def __init__(self, prefix, keys):
        self.prefix = prefix
        self.keys = keys

    def read(self) -> OrderedDict:
        environ = OrderedDict()
        client = boto3.client('ssm')
        for key in self.keys:
            result = client.get_parameter(Name=f'{self.prefix}{key}', WithDecryption=True)
            environ[key] = result['Parameter']['Value']
        return environ
