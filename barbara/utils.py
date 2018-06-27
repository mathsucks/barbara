import os
import sys
from collections.__init__ import OrderedDict

import click
from dotenv import find_dotenv

from . import __version__
from .reader import EnvVariable, EnvVariableTemplate


#: Default name to use for new files when none are discovered or given
DEFAULT_ENV_FILENAME = '.env'


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
        return create_target_file(target_file)
    else:
        click.echo('Cannot continue without target file', color='R')
        sys.exit(1)


def create_target_file(target_file: str = None) -> bool:
    """Creates an empty file at the target."""
    click.open_file(target_file, 'w').close()
    return target_file


def prompt_user_for_value(env_variable) -> str:
    """Prompts the user for a value for an EnvVariable or EnvVariableTemplate.

    If the variable contains subvariables, the user is prompted for each subvariable before the result is returned as
    a formatted string.
    """
    try:
        context = {prompt.name: prompt_user_for_value(prompt) for prompt in env_variable.subvariables}
        return env_variable.template.format(**context)
    except AttributeError:
        return click.prompt(env_variable.name, default=env_variable.preset, type=str)


def merge_with_prompts(existing: OrderedDict, template: OrderedDict, skip_existing: bool) -> OrderedDict:
    """Merge two ordered dicts and prompts the user for values along the way

    If skipping existing keys, only newly discovered keys will be prompted for. Once a key exists, the existing
    value will be given as a preset, when the key doesn't exist the template preset is presented. A template with a
    missing value is considered an error.
    """
    merged = existing.copy()

    template_keys = set(k.upper() for k in template.keys())
    existing_keys = set(k.upper() for k in existing.keys())

    keys = template_keys.difference(existing_keys) if skip_existing else template_keys

    for key in sorted(keys):
        preset = EnvVariable(key, existing.get(key)) if key in existing else template.get(key)
        merged[key] = prompt_user_for_value(preset)

    return OrderedDict(sorted(merged.items()))
