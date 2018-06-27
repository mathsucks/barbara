import re
from collections import OrderedDict, namedtuple

import boto3
from dotenv import dotenv_values



#: Regular environment variable with a preset value
EnvVariable = namedtuple('EnvVariable', ('name', 'preset', ), )

#: Complex environment variable with one or more subvariables which are used for templating values
EnvVariableTemplate = namedtuple('EnvVariableTemplate', ('name', 'template', 'subvariables', ), )


class Reader:
    """Reads environment variables from file into an ordered dictionary"""

    #: Regular expression for matching sub-variables to fill in
    VARIABLE_MATCHER = re.compile(r'(?P<variable>\[(?P<name>\w+)(:(?P<preset>\w+))?\])')

    def __init__(self, source):
        self.source = source

    @staticmethod
    def find_subvariables(preset: str) -> tuple:
        """Search a string for sub-variables and emit the matches as they are discovered"""
        for match in Reader.VARIABLE_MATCHER.finditer(preset):
            match_map = match.groupdict()
            yield EnvVariable(match_map['name'], match_map.get('preset', None))

    def _get_string_template(self, source: str) -> str:
        """Generate a python string template to populate with the subvariable results"""
        return self.VARIABLE_MATCHER.sub(r'{\2}', source)

    def _read(self) -> OrderedDict:
        try:
            return dotenv_values(self.source)
        except TypeError:
            return dotenv_values(self.source.name)

    def read(self) -> OrderedDict:
        environ = self._read()
        for key, preset in environ.items():
            subvariables = list(self.find_subvariables(preset))
            if subvariables:
                environ[key] = EnvVariableTemplate(key, self._get_string_template(preset), subvariables)
            else:
                environ[key] = EnvVariable(key, preset)
        return environ



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





