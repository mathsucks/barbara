from collections import namedtuple


#: Regular environment variable with a preset value
EnvVariable = namedtuple("EnvVariable", ("name", "preset"))

#: Complex environment variable with one or more subvariables which are used for templating values
EnvVariableTemplate = namedtuple(
    "EnvVariableTemplate", ("name", "template", "subvariables")
)
