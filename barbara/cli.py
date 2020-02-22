import os

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
@click.option("-d", "--destination", default="", type=str, help="Destination for serialized environment variables")
@click.option(
    "-t", "--template", default="env-template.yml", type=click.File(), help="Source for environment and default values"
)
@click.option(
    "-z", "--zero-input", is_flag=True, help="Skip prompts and use presets verbatim. Useful for CI environments."
)
@click.version_option(poetry_version.extract(source_file=__file__))
def barbara_develop(skip_existing, destination, template, zero_input):
    """Development mode which prompts for user input"""
    if zero_input:
        destination = ".env"
        destination_handler = create_target_file
        merge_strategy = merge_with_presets
    else:
        destination_handler = confirm_target_file
        merge_strategy = merge_with_prompts

    confirmed_target = destination if os.path.exists(destination) else destination_handler(destination)

    click.echo(f"Creating environment: {confirmed_target}")

    TemplateReader = readers.get_reader(template)
    environment_template = TemplateReader(template).read()
    existing_environment = readers.EnvReader(confirmed_target).read()
    click.echo(f"Skip Existing: {skip_existing}")

    environment = merge_strategy(existing_environment, environment_template["environment"], skip_existing)

    Writer(confirmed_target, environment).write()

    click.echo("Environment ready!")


@click.command()
@click.option(
    "-t", "--template", default="env-template.yml", type=click.File(), help="Template for environment variables"
)
@click.option("-o", "--output", default=".env", type=str, help="Destination for env-file")
@click.version_option(poetry_version.extract(source_file=__file__))
def barbara_deploy(output, template):
    """Deploy mode which retrieves values from AWS SSM"""
    confirmed_target = output if os.path.exists(output) else create_target_file(output)

    click.echo(f"Creating env-file: {confirmed_target}")

    config_reader = readers.YAMLTemplateReader(template)
    Writer(confirmed_target, config_reader.read()).write()

    click.echo("Environment ready!")
