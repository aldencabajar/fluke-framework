from typing import List
from click.testing import CliRunner
import pytest
from pathlib import Path
from fluke.core.config.datasets import Datasets, QueryDataset
from fluke.core.utils import cwd
from fluke.cli.dataset import dataset


@pytest.fixture
def dataset_config(project_directory: Path) -> Datasets:
    with cwd(project_directory):
        _datasets = Datasets()
    return _datasets


@pytest.mark.usefixtures('multiple_queries')
@pytest.mark.parametrize(
    'cli_args',
    [['--all'], ['--all', '-m'], ['stations'], ['address']]
)
def test_dataset_query(
    project_directory: Path, cli_runner: CliRunner,
    dataset_config: Datasets, cli_args: List[str]):

    args = ['query'] + cli_args

    with cwd(project_directory):
        results = cli_runner.invoke(dataset, args)
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


@pytest.mark.usefixtures('multiple_queries')
@pytest.mark.parametrize(
    'cli_args',
    [['--all'], ['stations'], ['address']]
)
def test_dataset_migrate(
    project_directory: Path,
    cli_runner: CliRunner,
    dataset_config: Datasets,
    cli_args: List[str]):

    args = ['migrate'] + cli_args

    with cwd(project_directory):
        results = cli_runner.invoke(dataset, args)
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
                _ds.delete_in_db()




