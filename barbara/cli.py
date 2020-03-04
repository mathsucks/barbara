from pathlib import Path

import click
import poetry_version

from . import readers
from .utils import confirm_target_file, create_target_file, merge_with_presets, merge_with_prompts
from .writers import Writer


@click.command()
@click.option(
    "-s",
    "--skip-existing",
    default=True,
    type=click.BOOL,
    help="Skip over any keys which already exist in the destination file",
)
@click.option("-o", "--output", default=".env", type=Path, help="Destination for env-file")
@click.option("-t", "--template", default="env-template.yml", type=Path, help="Template for environment variables")
@click.option(
    "-z", "--zero-input", is_flag=True, help="Skip prompts and use presets verbatim. Useful for CI environments."
)
@click.version_option(poetry_version.extract(source_file=__file__))
def barbara_develop(skip_existing, output, template, zero_input):
    """Development mode which prompts for user input"""
    if zero_input:
        destination_handler = create_target_file
        merge_strategy = merge_with_presets
    else:
        destination_handler = confirm_target_file
        merge_strategy = merge_with_prompts

    confirmed_target = Path(output if output.exists() else destination_handler(output))

    click.echo(f"Creating environment: {confirmed_target}")

    template_reader_class = readers.get_reader(template)
    environment_template = template_reader_class(template).read()
    existing_environment = readers.EnvReader(confirmed_target).read()
    click.echo(f"Skip Existing: {skip_existing}")

    environment = merge_strategy(existing_environment, environment_template["environment"], skip_existing)

    Writer(confirmed_target, environment).write()

    click.echo("Environment ready!")
