import click
from . import prompter
from . import reader


@click.command()
@click.option('--target', default=None)
@click.option('--skip-existing', default=True, type=click.BOOL)
@click.option('--template', default='.env.template', type=click.File())
def barbara(skip_existing, target, template):
    confimed_target = prompter.confirm_target_file(target)

    environment_template = reader.Reader(template).read()
    existing_environment = reader.Reader(confimed_target).read()

    if skip_existing:
        keys = set(environment_template.keys()).difference(existing_environment.keys())
    else:
        keys = environment_template.keys()

    for key in


if __name__ == '__main__':
    barbara()
