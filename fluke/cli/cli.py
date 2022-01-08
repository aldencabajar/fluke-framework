import click
from fluke.cli.project_create import create
from fluke.cli.pipeline import pipeline


@click.group()
def cli():
    pass


def main():
    cli.add_command(create)
    cli.add_command(pipeline)
    cli()
    # cli = click.CommandCollection(
    # sources=[create_cli, query_cli])


