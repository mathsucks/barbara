from fnmatch import fnmatch
from collections import ChainMap
from collections import OrderedDict
from collections import namedtuple
import re
from functools import partial

import boto3
from dotenv import dotenv_values
import yaml


#: Regular environment variable with a preset value
EnvVariable = namedtuple('EnvVariable', ('name', 'preset', ), )

#: Complex environment variable with one or more subvariables which are used for templating values
EnvVariableTemplate = namedtuple('EnvVariableTemplate', ('name', 'template', 'subvariables', ), )


def guess_reader_by_file_extension(filename):
    """Guess which reader to return using naive filetype check"""
    if any(map(partial(fnmatch, filename), ('*.yml', '*.yaml'))):
        return YAMLConfigReader
    else:
        return EnvTemplateReader


class EnvTemplateReader:
    """Reads environment variables from file into an ordered dictionary"""

    #: Regular expression for matching sub-variables to fill in
    VARIABLE_MATCHER = re.compile(r'(?P<variable>\[(?P<name>\w+)(:(?P<preset>\w+))?\])')

    def __init__(self, source):
        self.source = source

    @staticmethod
    def find_subvariables(preset: str) -> tuple:
        """Search a string for sub-variables and emit the matches as they are discovered"""
        for match in EnvTemplateReader.VARIABLE_MATCHER.finditer(preset):
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


class YAMLConfigReader:
    """Reads environment variables from YAML configuration into an ordered dictionary"""
    def __init__(self, source):
        self.source = source

    @staticmethod
    def find_subvariables(preset):
        try:
            for subvar_name, subvar_preset in preset['subvariables'].items():
                yield EnvVariable(subvar_name, subvar_preset)
        except TypeError:
            return None

    def _get_string_template(self, preset) -> str:
        """Get the string template from the preset"""
        return preset['template']

    def _read(self) -> OrderedDict:
        with open(self.source, 'r', encoding='utf8') as config_file:
            return yaml.load(config_file.read())

    def read(self) -> OrderedDict:
        environ = self._read()['environment']
        for key, preset in environ.items():
            subvariables = list(self.find_subvariables(preset))
            if subvariables:
                environ[key] = EnvVariableTemplate(key, self._get_string_template(preset), subvariables)
            else:
                environ[key] = EnvVariable(key, preset)
        return environ

    def generate_key_list_for_resource(self, resource_path):
        """Using the given resource path, generate a list of keys which respects the declared overrides.

        This is used for generating a tree which allows overriding the more generic hierarchy elements with
        more specific ones.

        For example, when the configuration contains the following:
            project: advanced

            environment:
              DEBUG: 1
              TEMPLATES: ../templates/
              ENVIRONMENT_NAME: development
              HOST_TYPE: local

            deployments:
              - DEBUG
              - TEMPLATES
              - staging:
                - DATABASE_URL
                - ENVIRONMENT_NAME
                - app_server:
                  - HOST_TYPE
                - worker:
                  - HOST_TYPE

        And the resource_path is:
            '/advanced/staging/worker'

        The result will be:
            [
                '/advanced/DEBUG',
                '/advanced/TEMPLATES',
                '/advanced/staging/DATABASE_URL',
                '/advanced/staging/ENVIRONMENT_NAME',
                '/advanced/staging/worker/HOST_TYPE',
            ]
        """
        yaml_config = self.read()
        variables = yaml_config['environment']['defaults']
        overrides = yaml_config['deployments']
        result = []
        path_segments = resource_path.split('/')
        for variable in variables:
            pass


class SSMReader:
    """Reads environment variables from AWS SSM storage into an ordered dictionary"""
    def __init__(self, key_list):
        self.key_list = key_list

    def read(self) -> OrderedDict:
        environ = OrderedDict()
        client = boto3.client('ssm')
        for key in self.key_list:
            result = client.get_parameter(Name=key, WithDecryption=True)
            environ[key.split('/')[-1]] = result['Parameter']['Value']
        return environ
