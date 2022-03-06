import click
from fluke.config.datasets import Datasets
from fluke.datasets.query_dataset import QueryDataset
from fluke.utils import RemoveRequire

@click.group(invoke_without_command = True)
@click.pass_context
def dataset(ctx: click.Context) -> None:
    """
    Manipulate and migrate datasets.
    """
    ds_config = Datasets()
    ctx.obj = ds_config

@dataset.command('query')
@click.option('--all', required=False, is_flag=True)
@click.option('--migrate', '-m', required=False, is_flag=True)
@click.argument('name', cls=RemoveRequire, remove_req_if='all', required=False)
@click.pass_obj
def query(ds_config: Datasets, name: str, all: bool, migrate: bool) -> None:
    """
        Query datasets with type `QueryDataset`.
    """
    if not ds_config.query_dataset_exists():
        raise click.UsageError(
            ('No query datasets found in `datasets.yaml`.'))
    if all:
        for _dataset in ds_config:
            if isinstance(_dataset, QueryDataset):
                _dataset.perform_query()
                if migrate:
                    _dataset.migrate()
    else:
        _dataset = ds_config[name]
        assert isinstance(_dataset, QueryDataset)
        _dataset.perform_query()
        if migrate:
            _dataset.migrate()


@dataset.command('migrate')
@click.option('--all', required=False, is_flag=True)
@click.argument('name', cls=RemoveRequire, remove_req_if='all', required=False)
@click.pass_obj
def migrate(ds_config: Datasets, name: str, all: bool) -> None:
    """Migrate tables from Databases defined with type `QueryDataset`."""
    if not ds_config.query_dataset_exists():
        raise click.UsageError(
            ('No query datasets found in `datasets.yaml`')
        )
    if all:
        for _dataset in ds_config:
            if isinstance(_dataset, QueryDataset):
                _dataset.migrate()
    else:
        _dataset = ds_config[name]
        assert isinstance(_dataset, QueryDataset)
        _dataset.migrate()












