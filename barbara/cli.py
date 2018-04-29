import click

from .utils import confirm_target_file, merge_with_prompts, print_version
from .reader import Reader
from .writer import Writer




@click.command()
@click.option('-s', '--skip-existing', default=True,
              type=click.BOOL, help='Skip over any keys which already exist in the destination file')
@click.option('-d', '--destination', default=None,
              type=click.File(), help='Destination for serialized environment variables')
@click.option('-t', '--template', default='.env.template',
              type=click.File(), help='Source for environment and default values')
@click.option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print version and exit.')
def barbara(skip_existing, destination, template):
    try:
        confirmed_target = destination.name
    except AttributeError:
        confirmed_target = confirm_target_file(destination)

    click.echo(f'Creating environment: {confirmed_target}')

    environment_template = Reader(template).read()
    existing_environment = Reader(confirmed_target).read()
    click.echo(f'Skip Existing: {skip_existing}')

    environment = merge_with_prompts(existing_environment, environment_template, skip_existing)

    Writer(confirmed_target, environment).write()

    click.echo('Environment ready!')
