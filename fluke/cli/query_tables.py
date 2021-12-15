from pathlib import Path
import re
import click
import os
from fluke.core.objects import Table
from fluke.core.config import Project
from fluke.core.utils import (
  find_root_proj,
  _find_create_scripts,
  get_table_names_click,
  RemoveRequire
)

ALL_HELP = """Run all create_* queries under src/data_pull"""
TBL_VERSION_HELP = """Version suffix to be used for created tables.
Can be keywords: `day`, `month`, `week`, or arbitrary string."""
TBL_VERSION_RECORD_HELP = """Record this table version."""



@click.group()
def table():
    pass

@table.command('create')
@click.argument('name', type=str, required=True)
def create(name: str):
    path_to_file = Path(find_root_proj(), 'src/data_pull', f'create_{name}.R')
    path_to_file.touch()
    click.echo((
        f'Created `{name}` script under `src/data_pull`.\n'
        'Make sure that the script outputs a string for query. '
        'Consider running `table query` afterwards.'
    ))


@table.command()
@click.option('--all', help = ALL_HELP, is_flag=True)
@click.option('--version', '-v', help= TBL_VERSION_HELP, required=False, default='day')
@click.option('--record','record', type = click.BOOL, help = TBL_VERSION_RECORD_HELP, is_flag = True)
@click.argument('table', type = str, required= False, cls= RemoveRequire, remove_req_if = 'all',
shell_complete = get_table_names_click)
def query(all: bool, table: str, version: str, record: bool) -> None:
    """
    Query CLI API
    using database config from project-config.yml, runs a database query
    from  src/data_pull with scripts with prefix `create_`. Table name
    is the suffix after `create_`.
    """
    proj_root = find_root_proj()
    create_scripts  = _find_create_scripts(proj_root)

    #Instantiate current project configuration
    project =  Project()

    # add new tables from create_scripts
    for  _src in create_scripts:
        _table = Table(_src)
        if _table.name not in project.tables():
            project.tables.add(_table)

    # run database query if all flag is TRUE
    if all:
        for _, tbl in project.tables().items():
            tbl.add(version)
            project.database.query(tbl.most_recent_ver())
    # run this code if single table is given
    else:
        tbl = project.tables.get(table)
        tbl.add(version)
        project.database.query(tbl.most_recent_ver())

    if record:
        project.write()

    # After querying, update the project config to reflect changes

