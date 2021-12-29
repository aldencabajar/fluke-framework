from typing import Generator, List
from click.testing import CliRunner, Result
import pytest
from pathlib import Path
from fluke.config.datasets import Datasets
from fluke.datasets.query_dataset import QueryDataset
from fluke.cli.dataset import dataset


@pytest.fixture
def dataset_config() -> Datasets:
    _datasets = Datasets()
    return _datasets

@pytest.fixture
def bq_queried_tables(dataset_config: Datasets, cli: CliRunner) -> Generator[Result, None, None]:

    try:
        results = cli.invoke(dataset, ['query', '--all'], echo=True)
        yield results
    finally:
        for _ds in dataset_config:
            if isinstance(_ds, QueryDataset):
                _ds.delete_in_db()


@pytest.mark.usefixtures('multiple_queries')
@pytest.mark.parametrize(
    'cli_args',
    [['--all'], ['--all', '-m'], ['stations'], ['address']]
)
def test_dataset_query(cli: CliRunner, dataset_config: Datasets, cli_args: List[str]):
    args = ['query'] + cli_args

    results = cli.invoke(dataset, args, echo=True)
    assert results.exit_code == 0

    if '--all' in cli_args:
        for _ds in dataset_config:
            if isinstance(_ds, QueryDataset):
                assert _ds.exists_in_db()
                if ['--all', '-m'] == cli_args:
                    assert _ds.params.version is not None
                    assert Path(
                        _ds.params.location,
                        _ds.params.version).exists()
                _ds.delete_in_db()
    else:
        _ds = dataset_config[cli_args[0]]
        assert isinstance(_ds, QueryDataset)
        assert _ds.exists_in_db()


@pytest.mark.usefixtures('multiple_queries', 'bq_queried_tables')
@pytest.mark.parametrize(
    'cli_args',
    [['--all'], ['stations'], ['address']]
)
def test_dataset_migrate(cli: CliRunner, dataset_config: Datasets, cli_args: List[str]):
    args = ['migrate'] + cli_args

    results = cli.invoke(dataset, args, echo=True)
    assert results.exit_code == 0

    for _ds in dataset_config:
        if isinstance(_ds, QueryDataset):
            if '--all' not in cli_args or _ds.name not in cli_args:
                pass
            p = _ds.params
            if p.version is not None:
                path_to_tbl = Path(p.location, p.version)
            assert path_to_tbl.exists()
            assert _ds.exists_in_db()




