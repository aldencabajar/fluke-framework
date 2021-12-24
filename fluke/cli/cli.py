import click
from fluke.cli.project_create import create


@click.group()
def cli():
    pass


def main():
    cli.add_command(create)
    cli()
    # cli = click.CommandCollection(
    # sources=[create_cli, query_cli])


