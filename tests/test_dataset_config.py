from fluke.core.config import Datasets
from fluke.core.utils import cwd,run_r
from pathlib import Path
import pytest
import yaml

@pytest.fixture
def dataset_csv(project_directory: Path):
    # get data from R, iris dataset
    path_to_csv = Path(
        project_directory,
        'datasets',
        'iris_sample_data.csv'
    )
    cmd = f"""
    data(iris)
    write.csv(iris, file = '{str(path_to_csv)}')
    """
    run_r(cmd, ['-e'])

    # write datasets yaml
    path_to_ds_config = Path(project_directory, 'config', 'datasets.yaml')
    yaml_payload = """
    datasets:
        iris:
            type: csv
            params:
                location: iris_sample_data.csv
    """

    with path_to_ds_config.open('w', encoding='utf-8') as config:
        yaml.safe_dump(yaml.safe_load(yaml_payload), config)

    return path_to_csv

@pytest.fixture
def _version() -> str:
    return 'test_version'


def test_dataset_config_init(
    dataset_csv: Path,
    project_directory: Path,
    _version: str):
    """Basic test to see if config initialization works."""

    assert dataset_csv.exists()

    with cwd(project_directory):
        datasets = Datasets(_version)

    assert len(datasets) == 1

def test_dataset_targets_run(
    dataset_csv: Path,
    project_directory: Path,
    _version: str):

    assert dataset_csv.exists()

    with cwd(project_directory):
        datasets = Datasets(_version)
        datasets.run_targets_cmd()
        assert Path('datasets', 'stores', _version).exists()





