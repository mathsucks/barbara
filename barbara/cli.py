import os

import click

from .readers import EnvTemplateReader
from .readers import SSMReader
from .utils import confirm_target_file
from .utils import create_target_file
from .utils import merge_with_prompts
from .utils import print_version
from .writers import Writer


@click.command()
@click.option('-s', '--skip-existing', default=True, type=click.BOOL, help='Skip over any keys which already exist in the destination file')
@click.option('-d', '--destination', default='', type=str, help='Destination for serialized environment variables')
@click.option('-t', '--template', default='.env.yml', type=click.File(), help='Source for environment and default values')
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Print version and exit.')
def barbara_develop(skip_existing, destination, template):
    """Development mode which prompts for user input"""
    confirmed_target = destination if os.path.exists(destination) else confirm_target_file(destination)

    click.echo(f'Creating environment: {confirmed_target}')
    import pdb;pdb.set_trace()

    environment_template = EnvTemplateReader(template).read()
    existing_environment = EnvTemplateReader(confirmed_target).read()
    click.echo(f'Skip Existing: {skip_existing}')

    environment = merge_with_prompts(existing_environment, environment_template, skip_existing)

    Writer(confirmed_target, environment).write()

    click.echo('Environment ready!')



@click.command()
@click.option('-d', '--destination', default='.env', type=str, help='Destination for serialized environment variables')
@click.option('-t', '--template', default='.env.template', type=click.File(), help='Source for environment variable keys')
@click.option('-p', '--prefix', default='', type=str, help='Key prefix to apply when looking up values')
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Print version and exit.')
def barbara_deploy(destination, template, prefix):
    """Deploy mode which retrieves values from AWS SSM"""
    confirmed_target = destination if os.path.exists(destination) else create_target_file(destination)

    click.echo(f'Creating environment: {confirmed_target}')

    environment_template = EnvTemplateReader(template).read()
    environment = SSMReader(prefix, environment_template.keys()).read()

    Writer(confirmed_target, environment).write()

    click.echo('Environment ready!')
