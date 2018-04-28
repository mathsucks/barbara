import os
import sys

import click
from dotenv import find_dotenv

DEFAULT_ENV_FILENAME = '.env'


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
        open(target_file, 'w').close()
        return True
    else:
        click.echo('Cannot continue without target file', color='R')
        sys.exit(1)


def get_key_value_pair(key: str, default: str='') -> tuple:
    """Prompts the user for a value and provides an optional default"""
    return click.prompt(key, default=default, type=str)
