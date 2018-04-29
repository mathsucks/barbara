import os
import re
import sys
from collections.__init__ import OrderedDict

import click
from dotenv import find_dotenv

DEFAULT_ENV_FILENAME = '.env'
VARIABLE_MATCHER = re.compile(r'(?P<variable>\[(?P<var_name>\w+)(:(?P<default>\w+))?\])')


def confirm_target_file(target_file: str = None) -> bool:
    """Determines which target file to use.

    Strategy progresses as follows:
        - Confirm the provided value
        - Search for one automatically, then confirm
        - Offer to create one
        - Quit
    """
    target_file = target_file or find_dotenv() or DEFAULT_ENV_FILENAME

    if os.path.exists(target_file):
        return click.prompt('Destination file', default=target_file)
    elif click.confirm(f'{target_file} does not exist. Create it', prompt_suffix='? '):
        click.open_file(target_file, 'w').close()
        return target_file
    else:
        click.echo('Cannot continue without target file', color='R')
        sys.exit(1)


def get_key_value_pair(key: str, default: str='') -> tuple:
    """Prompts the user for a value and provides an optional default"""
    if VARIABLE_MATCHER.match(default):
        click.secho(f'{key}:', fg='green')
        result = default
        for variable, var_name, var_default in find_variables(default):
            result = result.replace(variable, click.prompt(var_name, default=var_default))
        return result
    else:
        return click.prompt(key.upper(), default=default, type=str)


def find_variables(template) -> tuple:
    for match in VARIABLE_MATCHER.finditer(template):
        match_map = match.groupdict()
        yield match['variable'], match_map['var_name'], match_map.get('default', None)


def merge_with_prompts(existing: OrderedDict, template: OrderedDict, skip_existing: bool) -> OrderedDict:
    merged = existing.copy()

    template_keys = set(k.upper() for k in template.keys())
    existing_keys = set(k.upper() for k in existing.keys())

    keys = template_keys.difference(existing_keys) if skip_existing else template_keys

    for key in keys:
        default = existing.get(key, template[key])
        merged[key] = get_key_value_pair(key, default)

    return merged
