import os
import sys
from pathlib import Path
from typing import Dict, List, Union

import click

from .variables import AutoVariable, EnvVariable

EMPTY = object()


def confirm_target_file(target_file: Path = None) -> bool:
    """Determines which target file to use.

    Strategy progresses as follows:
        - Confirm the provided value
        - Offer to create one
        - Quit
    """
    if target_file.exists():
        return click.prompt("Destination file", default=target_file.relative_to(os.getcwd()))
    if click.confirm(f"{target_file} does not exist. Create it?"):
        return create_target_file(target_file)

    click.echo("Cannot continue without target file", color="R")
    sys.exit(1)


def create_target_file(target_file: Path = None) -> bool:
    """Creates an empty file at the target."""
    target_file.touch()
    return target_file


def prompt_user_for_value(env_variable: EnvVariable) -> str:
    """Prompts the user for a value for an EnvVariable."""
    return click.prompt(env_variable.name, default=env_variable.preset, type=str)


def merge_keys(
    existing: Dict[str, str], template: Dict[str, Union[EnvVariable, AutoVariable]], skip_existing: bool
) -> List[str]:
    """Merge existing values with template values."""
    template_keys = set(k.upper() for k in template.keys())
    existing_keys = set(k.upper() for k in existing.keys())
    auto_var_keys = set(k.upper() for k in template.keys() if isinstance(template.get(k), AutoVariable))

    merged_keys = template_keys - existing_keys if skip_existing else template_keys

    # Always append AutoVariable keys for regeneration
    merged_keys |= auto_var_keys

    return sorted(merged_keys)


def merge_with_presets(
    existing: Dict[str, str], template: Dict[str, Union[EnvVariable, AutoVariable]], skip_existing: bool
) -> Dict[str, str]:
    """Merge two ordered dicts and uses the presets for values along the way

    If skipping existing keys, only newly discovered keys will be added. Once a key exists, the existing
    value will be used as the preset, when the key doesn't exist the template preset is assigned.
    """
    merged = existing.copy()

    for key in merge_keys(existing, template, skip_existing):
        if isinstance(template.get(key), AutoVariable):
            merged[key] = template[key].generate()
        elif existing.get(key, EMPTY) is not EMPTY:
            merged[key] = existing.get(key)
        elif isinstance(template.get(key), EnvVariable):
            merged[key] = template[key].preset
        else:
            raise TypeError(f"Unrecognized variable type: {template[key]}")

    return dict(sorted(merged.items()))


def merge_with_prompts(
    existing: Dict[str, str], template: Dict[str, Union[EnvVariable, AutoVariable]], skip_existing: bool
) -> Dict[str, str]:
    """Merge two ordered dicts and prompts the user for values along the way

    If skipping existing keys, only newly discovered keys will be prompted for. Once a key exists, the existing
    value will be given as a preset, when the key doesn't exist the template preset is presented.
    """
    merged = existing.copy()

    for key in merge_keys(existing, template, skip_existing):
        if isinstance(template.get(key), AutoVariable):
            merged[key] = template[key].generate()
        else:
            variable = EnvVariable(key, existing.get(key)) if key in existing else template.get(key)
            merged[key] = prompt_user_for_value(variable)

    return dict(sorted(merged.items()))
