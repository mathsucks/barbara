import click

from .utils import confirm_target_file, merge_with_prompts
from .reader import Reader
from .writer import Writer


@click.command()
@click.option('--skip-existing', default=True, type=click.BOOL)
@click.option('--target', default=None, type=click.File())
@click.option('--template', default='.env.template', type=click.File())
def barbara(skip_existing, target, template):
    try:
        confirmed_target = target.name
    except AttributeError:
        confirmed_target = confirm_target_file(target)

    click.echo(f'Creating environment: {confirmed_target}')

    environment_template = reader.Reader(template).read()
    existing_environment = reader.Reader(confirmed_target).read()
    click.echo(f'Skip Existing: {skip_existing}')

    environment = merge_with_prompts(existing_environment, environment_template, skip_existing)

    writer.Writer(confirmed_target, environment).write()

    click.echo('Environment ready!')


if __name__ == '__main__':
    barbara()
