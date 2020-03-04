import abc
import subprocess
from collections import namedtuple

#: Regular environment variable with a preset value
EnvVariable = namedtuple("EnvVariable", ("name", "preset"))


class AutoVariable(metaclass=abc.ABCMeta):
    """AutoVariables do not require user input and are always updated when generating a new env-file."""

    def validate(self) -> bool:
        """Validate template parameters, if necessary."""
        return NotImplemented

    def generate(self) -> str:
        """Generate value for AutoVariable."""
        return NotImplemented


class GitCommitVariable(AutoVariable):
    """Replaced with git commit hash when generating an env-file."""

    def __init__(self, name: str, length: int):
        self.name = name
        self.length = int(length)

    def __eq__(self, other):
        return all((self.name == other.name, self.length == other.length))

    def validate(self):
        """Length must be an integer and request less than or equal to 40 characters."""
        assert isinstance(self.length, int) and self.length <= 40

    def generate(self):
        """Generate Git commit hash of requested length."""
        try:
            git_revision = subprocess.check_output(["git", "rev-parse", "HEAD"])
            hash_size = slice(0, self.length)
            return git_revision[hash_size]
        except subprocess.CalledProcessError:
            return "UNKNOWN"
