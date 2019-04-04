import os

import click

from . import readers
from .utils import confirm_target_file
from .utils import create_target_file
from .utils import merge_with_presets
from .utils import merge_with_prompts
from .utils import print_version
from .writers import Writer


@click.command()
@click.option(
    "-s",
    "--skip-existing",
    default=True,
    type=click.BOOL,
    help="Skip over any keys which already exist in the destination file",
)  # noqa
@click.option(
    "-d",
    "--destination",
    default="",
    type=str,
    help="Destination for serialized environment variables",
)
@click.option(
    "-t",
    "--template",
    default=".env.yml",
    type=click.File(),
    help="Source for environment and default values",
)  # noqa
@click.option(
    "-z",
    "--zero-input",
    is_flag=True,
    help="Skip prompts and use presets verbatim. Useful for CI environments.",
)  # noqa
@click.option(
    "-v",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Print version and exit.",
)  # noqa
def barbara_develop(skip_existing, destination, template, zero_input):
    """Development mode which prompts for user input"""
    if zero_input:
        destination = ".env"
        destination_handler = create_target_file
        merge_strategy = merge_with_presets
    else:
        destination_handler = confirm_target_file
        merge_strategy = merge_with_prompts

    confirmed_target = (
        destination if os.path.exists(destination) else destination_handler(destination)
    )

    click.echo(f"Creating environment: {confirmed_target}")

    TemplateReader = readers.guess_reader_by_file_extension(template)
    environment_template = TemplateReader(template).read()
    existing_environment = readers.EnvReader(confirmed_target).read()
    click.echo(f"Skip Existing: {skip_existing}")

    environment = merge_strategy(
        existing_environment, environment_template, skip_existing
    )

    Writer(confirmed_target, environment).write()

    click.echo("Environment ready!")


@click.command()
@click.option(
    "-d",
    "--destination",
    default=".env",
    type=str,
    help="Destination for serialized environment variables",
)
@click.option(
    "-t",
    "--template",
    default=".env.yml",
    type=click.File(),
    help="Source for environment variable keys",
)
@click.option(
    "-p",
    "--search-path",
    required=True,
    type=str,
    help="Search path to use for SSM environment variables",
)
@click.option(
    "-v",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Print version and exit.",
)  # noqa
def barbara_deploy(destination, template, search_path):
    """Deploy mode which retrieves values from AWS SSM"""
    confirmed_target = (
        destination if os.path.exists(destination) else create_target_file(destination)
    )

    click.echo(
        f"Creating environment: {confirmed_target} (using search_path: {search_path})"
    )

    config_reader = readers.YAMLConfigReader(template)
    key_list = config_reader.generate_key_list_for_resource(search_path)
    environment = readers.SSMReader(key_list).read()

    Writer(confirmed_target, environment).write()

    click.echo("Environment ready!")
