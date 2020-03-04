from collections import namedtuple

#: Regular environment variable with a preset value
EnvVariable = namedtuple("EnvVariable", ("name", "preset"))

#: Replaced with git commit hash when generating an env-file
GitCommitPlaceholder = namedtuple("GitCommitPlaceholder", ("name", "length"))

#: Replaced with timestamp when generating an env-file
TimestampPlaceholder = namedtuple("TimestampPlaceholder", ("name", "format"))
