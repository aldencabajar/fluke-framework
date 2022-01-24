import os
import sys
import re
import json
import string
from typing import Optional
from click.termui import prompt
import fluke
from functools import wraps
from pathlib import Path
import click
from cookiecutter.main import cookiecutter
from tempfile import TemporaryDirectory
from distutils.dir_util import copy_tree
from fluke.utils import (
  get_cookiecutter_cfg,
  cwd,
  run_r
  )

template_dir = Path(
    Path(fluke.__file__).parent,
    'templates',
    'project'
)

config_path = get_cookiecutter_cfg(template_dir)
with config_path.open('r', encoding='utf-8') as file:
    config = json.load(file)


@click.group()
def create_cli() -> None:
    pass


def _project_cleanup(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (SystemExit, Exception) as error:
            click.echo(error)
    return wrapper

def _is_pkgname_valid(pkg_name: str) -> bool:
    # valid characters
    _chars = string.ascii_lowercase
    for chr in pkg_name:
        if chr not in _chars:
            raise click.UsageError(
                ('Package name must only contain lowercase letters.'
                )
            )
    return True

def _is_projname_valid(proj_name: str) -> bool:
    # valid characters
    _chars = re.escape(string.ascii_lowercase + '_-')
    for chr in proj_name:
        if chr not in _chars:
            raise Exception(
                ('Project name must only contain '
                'lowercase letters and `_|-`.'
                )
            )
    return True


@create_cli.command()
@click.option("--path", "-p", "path", default=str(Path.cwd()))
@click.option('--pkg_name', required=False)
@click.argument("project_name", required=False)
@_project_cleanup
def create(path: str, pkg_name: Optional[str], project_name: Optional[str]) -> None:
    """
    CLI command to create a Fluke project.
    """
    if project_name is None:
        project_name = click.prompt('Name of project')
    _is_projname_valid(project_name)

    if pkg_name is None:
        pkg_name = click.prompt('Name of R package')
    _is_pkgname_valid(pkg_name)

    # add needed settings to config file
    config['project_name'] = project_name
    config['pkg_name'] = pkg_name
    config['python_path'] = sys.executable

    # create a tempdir to copy config and relevant template files
    with TemporaryDirectory(prefix='fluke') as temp_dir:
        ck_dir = '{{cookiecutter.project_name}}'
        copy_tree(
            str(Path(template_dir, ck_dir)),
            str(Path(temp_dir, ck_dir))
        )

        json_path = Path(temp_dir, 'cookiecutter.json')
        with json_path.open('w', encoding='utf-8') as json_file:
            json.dump(config, json_file)

        # use cookiecutter to transform template to dir with info
        path_to_output = Path(path).expanduser()
        path_to_project = Path(path_to_output, Path(project_name))
        cookiecutter(str(temp_dir), output_dir=str(path_to_output), no_input=True)
        click.echo(f'Created project "{project_name}" at "{str(path_to_output)}"')

    with cwd(path_to_project):
        # run project initialization
        click.echo('Initializing project using renv ...')
        run_r(
            """
            source('renv/activate.R')
            renv::restore()
            """,
            flags=['--vanilla', '-e']
        )

        # Initialize git
        click.echo('Initializing git inside project...')
        os.system('git init')
    click.echo('Finished initializing!')

