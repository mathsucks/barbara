from collections import OrderedDict
from fnmatch import fnmatch
from functools import partial
import re
from typing import Generator
from typing import List
from typing import TextIO
from typing import Type
from typing import Union

import boto3
from dotenv import dotenv_values
import yaml

from .utils import find_most_specific_match
from .utils import key_list_generator
from .variables import EnvVariable
from .variables import EnvVariableTemplate


def guess_reader_by_file_extension(file_or_name: Union[str, TextIO]) -> Type:
    """Guess which reader to return using naive filetype check"""
    filename = getattr(file_or_name, "name", file_or_name)
    filename_matcher = partial(fnmatch, filename)
    yaml_extensions = ("*.yml", "*.yaml")
    if any(filename_matcher(extension) for extension in yaml_extensions):
        return YAMLConfigReader
    else:
        return EnvTemplateReader


class EnvReader:
    """Reads environment variables from file into an ordered dictionary"""

    def __init__(self, source: Union[str, TextIO]) -> None:
        self.source = source

    def read(self) -> OrderedDict:
        filename = getattr(self.source, "name", self.source)
        return dotenv_values(filename)


class EnvTemplateReader(EnvReader):
    """Reads environment variable template from file into an ordered dictionary"""

    #: Regular expression for matching sub-variables to fill in
    VARIABLE_MATCHER = re.compile(r"(?P<variable>\[(?P<name>\w+)(:(?P<preset>\w+))?\])")

    @staticmethod
    def find_subvariables(preset: str) -> Generator[EnvVariable, None, None]:
        """Search a string for sub-variables and emit the matches as they are discovered"""
        for match in EnvTemplateReader.VARIABLE_MATCHER.finditer(preset):
            match_map = match.groupdict()
            yield EnvVariable(match_map["name"], match_map.get("preset", None))

    def _get_string_template(self, source: str) -> str:
        """Generate a python string template to populate with the subvariable results"""
        return self.VARIABLE_MATCHER.sub(r"{\2}", source)

    def read(self) -> OrderedDict:
        environ = super(EnvTemplateReader, self).read()
        for key, preset in environ.items():
            subvariables = list(self.find_subvariables(preset))
            if subvariables:
                environ[key] = EnvVariableTemplate(
                    key, self._get_string_template(preset), subvariables
                )
            else:
                environ[key] = EnvVariable(key, preset)
        return environ


class YAMLConfigReader:
    """Reads environment variables from YAML configuration into an ordered dictionary"""

    def __init__(self, source: TextIO) -> None:
        self.source = source

    @staticmethod
    def find_subvariables(
        preset: EnvVariableTemplate
    ) -> Generator[EnvVariable, None, None]:
        try:
            for subvar_name, subvar_preset in preset["subvariables"].items():
                yield EnvVariable(subvar_name, subvar_preset)
        except TypeError:
            return None

    def _get_string_template(self, preset: EnvVariableTemplate) -> str:
        """Get the string template from the preset"""
        return preset["template"]

    def _read(self) -> OrderedDict:
        return yaml.load(self.source.read())

    def read(self) -> OrderedDict:
        environ = self._read()["environment"]
        for key, preset in environ.items():
            subvariables = list(self.find_subvariables(preset))
            if subvariables:
                environ[key] = EnvVariableTemplate(
                    key, self._get_string_template(preset), subvariables
                )
            else:
                environ[key] = EnvVariable(key, preset)
        return environ

    def generate_key_list_for_resource(self, resource_path: str):
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
        yaml_config = self._read()
        yaml_variables = yaml_config["environment"]
        yaml_overrides = yaml_config["deployments"]

        overrides = list(
            key_list_generator(yaml_overrides, f'/{yaml_config["project"]}')
        )
        return [
            find_most_specific_match(v, resource_path, overrides)
            for v in yaml_variables.keys()
        ]


class SSMReader:
    """Reads environment variables from AWS SSM storage into an ordered dictionary"""

    def __init__(self, key_list: List[str]) -> None:
        self.key_list = key_list

    def read(self) -> OrderedDict:
        environ = OrderedDict()  # noqa
        client = boto3.client("ssm")
        for key in self.key_list:
            result = client.get_parameter(Name=key, WithDecryption=True)
            environ[key.split("/")[-1]] = result["Parameter"]["Value"]
        return environ
