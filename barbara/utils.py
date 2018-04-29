import os
import re
import sys
from collections.__init__ import OrderedDict

import click
from dotenv import find_dotenv

from . import __version__


#: Default name to use for new files when none are discovered or given
DEFAULT_ENV_FILENAME = '.env'

#: Regular expression for matching sub-variables to fill in
VARIABLE_MATCHER = re.compile(r'(?P<variable>\[(?P<var_name>\w+)(:(?P<default>\w+))?\])')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'Barbara v{__version__}')
    ctx.exit()


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
    elif click.confirm(f'{target_file} does not exist. Create it?'):
        click.open_file(target_file, 'w').close()
        return target_file
    else:
        click.echo('Cannot continue without target file', color='R')
        sys.exit(1)


def get_value_for_key(key: str, default: str = '') -> str:
    """Prompts the user for a value and provides an optional default

    If the default contains sub-variables, the user is shown the key name and then prompted for each segment.
    Sub-variables can also contain defaults.
    """
    if VARIABLE_MATCHER.match(default):
        click.secho(f'{key}:', fg='green')
        result = default
        for variable, var_name, var_default in find_subvariables(default):
            result = result.replace(variable, click.prompt(var_name, default=var_default))
        return result
    else:
        return click.prompt(key, default=default, type=str)


def find_subvariables(value: str) -> tuple:
    """Search a string for sub-variables and emit the matches as they are discovered"""
    for match in VARIABLE_MATCHER.finditer(value):
        match_map = match.groupdict()
        yield match['variable'], match_map['var_name'], match_map.get('default', None)


def merge_with_prompts(existing: OrderedDict, template: OrderedDict, skip_existing: bool) -> OrderedDict:
    """Merge two ordered dicts and prompts the user for values along the way

    If skipping existing keys, only newly discovered keys will be prompted for. Once a key exists, the existing
    value will be given as a default, when the key doesn't exist the template default is presented. A template with a
    missing value is considered an error.
    """
    merged = existing.copy()

    template_keys = set(k.upper() for k in template.keys())
    existing_keys = set(k.upper() for k in existing.keys())

    keys = template_keys.difference(existing_keys) if skip_existing else template_keys

    for key in sorted(keys):
        default = existing.get(key, template[key])
        merged[key] = get_value_for_key(key, default)

    return OrderedDict(sorted(merged.items()))
