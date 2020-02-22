import os
import sys
from pathlib import Path
from typing import Dict

import click
from dotenv import find_dotenv

from .variables import EnvVariable

#: Default name to use for new files when none are discovered or given
DEFAULT_ENV_FILENAME = ".env"

EMPTY = object()


def confirm_target_file(target_file: Path = None) -> bool:
    """Determines which target file to use.

    Strategy progresses as follows:
        - Confirm the provided value
        - Search for one automatically, then confirm
        - Offer to create one
        - Quit
    """
    target_file = Path(target_file or find_dotenv() or DEFAULT_ENV_FILENAME)

    if target_file.exists():
        return click.prompt("Destination file", default=target_file.relative_to(os.getcwd()))
    elif click.confirm(f"{target_file} does not exist. Create it?"):
        return create_target_file(target_file)
    else:
        click.echo("Cannot continue without target file", color="R")
        sys.exit(1)


def create_target_file(target_file: Path = None) -> bool:
    """Creates an empty file at the target."""
    target_file.touch()
    return target_file


def prompt_user_for_value(env_variable) -> str:
    """Prompts the user for a value for an EnvVariable or EnvVariableTemplate.

    If the variable contains subvariables, the user is prompted for each subvariable before the result is returned as
    a formatted string.
    """
    try:
        click.echo(f"{env_variable.name} ({env_variable.template}):")
        context = {prompt.name: prompt_user_for_value(prompt) for prompt in env_variable.subvariables}
        return env_variable.template.format(**context)
    except AttributeError:
        return click.prompt(env_variable.name, default=env_variable.preset, type=str)


def merge_with_presets(existing: Dict, template: Dict, skip_existing: bool) -> Dict:
    """Merge two ordered dicts and uses the presets for values along the way

    If skipping existing keys, only newly discovered keys will be added. Once a key exists, the existing
    value will be used as the preset, when the key doesn't exist the template preset is assigned.
    """
    merged = existing.copy()

    template_keys = set(k.upper() for k in template.keys())
    existing_keys = set(k.upper() for k in existing.keys())

    keys = template_keys.difference(existing_keys) if skip_existing else template_keys

    for key in sorted(keys):
        if existing.get(key, EMPTY) is not EMPTY:
            existing_value = EnvVariable(key, existing.get(key))
        else:
            existing_value = template.get(key)

        if isinstance(existing_value, EnvVariable):
            merged[key] = existing_value.preset
        else:
            merged[key] = existing_value.template.format(**{k: v for k, v in existing_value.subvariables})

    return dict(sorted(merged.items()))


def merge_with_prompts(existing: Dict, template: Dict, skip_existing: bool) -> Dict:
    """Merge two ordered dicts and prompts the user for values along the way

    If skipping existing keys, only newly discovered keys will be prompted for. Once a key exists, the existing
    value will be given as a preset, when the key doesn't exist the template preset is presented.
    """
    merged = existing.copy()

    template_keys = set(k.upper() for k in template.keys())
    existing_keys = set(k.upper() for k in existing.keys())

    keys = template_keys.difference(existing_keys) if skip_existing else template_keys

    for key in sorted(keys):
        preset = EnvVariable(key, existing.get(key)) if key in existing else template.get(key)
        merged[key] = prompt_user_for_value(preset)

    return dict(sorted(merged.items()))
