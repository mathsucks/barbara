import re
from fnmatch import fnmatch
from functools import partial
from pathlib import Path
from typing import Dict, TextIO, Type, Union

import yaml
from click import FileError
from dotenv import dotenv_values

from .variables import EnvVariable

TEMPLATE_READERS = []


class BaseTemplateReader:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        TEMPLATE_READERS.append(cls)


def get_reader(file_or_name: Path) -> Type:
    """Guess which reader to return using naive file-type check"""
    filename = getattr(file_or_name, "name", file_or_name)
    filename_matcher = partial(fnmatch, filename)
    yaml_extensions = ("*.yml", "*.yaml")
    if any(filename_matcher(extension) for extension in yaml_extensions):
        for reader_class in TEMPLATE_READERS:
            try:
                reader_class(file_or_name).read()
                return reader_class
            except FileError:
                pass
    raise FileError("Unknown template type")


class EnvReader:
    """Read environment variables from file into an ordered dictionary"""

    def __init__(self, source: Union[str, TextIO]) -> None:
        self.source = source

    def read(self) -> Dict[str, str]:
        filename = getattr(self.source, "name", self.source)
        return dotenv_values(filename)


class YAMLTemplateReader(BaseTemplateReader):
    """Reads environment variables from YAML configuration into an ordered dictionary"""

    SCHEMA_VERSION_MATCH = r"^2(.0)*$"

    def __init__(self, source: TextIO) -> None:
        self.source = source

    def _read(self) -> Dict:
        """Check configuration file for acceptable versions."""
        source = yaml.safe_load(Path(self.source).read_text())
        assert source, self.source
        try:
            if re.match(self.SCHEMA_VERSION_MATCH, str(source["schema-version"])):
                return source
            else:
                raise TypeError
        except TypeError:
            raise TypeError(f"Version mismatch. Required 2, found: {source.get('schema-version')}")

    def read(self) -> Dict[str, str]:
        template = self._read()
        for key, preset in template["environment"].items():
            template["environment"][key] = EnvVariable(key, preset)
        return template
