from typing import List, Union
import click
from fluke.core.config import Project
from fluke.core.objects import Dataset
from fluke.core.utils import (
    Cadence,
    RemoveRequireOpt,
    RemoveRequire,
)


MIGRATE_ALL_HELP = 'Transfer all tables in dataset to local storage/cache.'


@click.group(invoke_without_command=True)
@click.option('--list', 'list_datasets', is_flag=True)
@click.pass_context
def dataset(ctx: click.Context, list_datasets: bool):
    """"Command-line interace for relevant methods for datasets."""
    # Instantiate project config
    project = Project()
    ctx.obj = project

    if list_datasets:
        if len(project.datasets()) == 0:
            raise Exception(
               ('No datasets found, consider adding one ',
               'using `dataset create.`')
            )
        for _ds_name, _ in project.datasets().items():
            print(_ds_name)


@dataset.command('create')
@click.option('--version', '-v', required=False)
@click.argument('name', cls=RemoveRequire, remove_req_if='version', required=False)
@click.pass_obj
def create(proj_config: Project, name: str, version: str):
    if version is not None:
        name = Cadence(version).version()
    _dataset = Dataset(name)
    proj_config.datasets.add(_dataset)

    _dataset.create_dataset_dir()

    proj_config.write()
    print(
        f'Successfully created dataset `{_dataset.name}`.',
        'record table version in dataset via `dataset migrate.`'
    )


@dataset.command('restore')
@click.option('--all', required=False)
@click.pass_obj
def restore(proj_config: Project, name: str, all: bool):
    """restore dataset objects from project config."""
    ...


@dataset.command('migrate')
@click.option('--all', help = MIGRATE_ALL_HELP, is_flag=True)
@click.option('--version', '-v', required=False, multiple=True, default=[])
@click.option('--table', '-t', cls=RemoveRequireOpt, remove_req_if='all',
required=True, multiple=True)
@click.argument('dataset_name', required=True)
@click.pass_obj
def migrate(project: Project, all: bool,
version: List[str], table: List[str],
dataset_name: str):
    """Transfer tables from a database to local storage (dataset)."""
    _dataset_obj = project.datasets.get(dataset_name)

    if all:
        if len(project.tables()) == 0:
            raise click.UsageError(
                ('No tables found. Add one using `table query`.')
            )
    # migrate every table, with current versions
        for _, _table in project.tables().items():
            _tbl_ver = _table.most_recent_ver()
            project.database.migrate(_dataset_obj, _tbl_ver)

    else:
    # code to migrate individuabl table versions
        tbl_ver_len_eq = len(table) == len(version)

        if not tbl_ver_len_eq and len(version) > 1:
            raise click.UsageError(
                ('Provide a single `version` str or list of versions with same'
                ' length as table.')
            )

        for i, tbl_name in enumerate(table):
            _table = project.tables.get(tbl_name)
            if len(version) == 0:
            # if no version was given, use the most recent version
                _tbl_ver = _table.most_recent_ver()
            elif len(version) == 1:
            # if only one version is given, use that version
                _tbl_ver = _table.get(version[0])
            elif len(version) > 1:
            # map table name to version
                _tbl_ver = _table.get(version[i])
            project.database.migrate(_dataset_obj, _tbl_ver)

    project.write()




if __name__ == '__main__':
    import os
    os.chdir('test-project')
    dataset()



