import yaml
import pytest
from pathlib import Path
from fluke.core.config import Datasets
from fluke.core.config.datasets import BigQueryDataset, CSVDataset
from fluke.core.utils import cwd, run_r
from .utils import add_datasets_yaml_payload

@pytest.fixture
def dataset_config_path(project_directory: Path) -> Path:
    return Path(project_directory, 'config', 'datasets.yaml')

@pytest.fixture
def _version() -> str:
    return 'test_version'

@pytest.fixture
def dataset_csv(project_directory: Path,
    dataset_config_path: Path,
    _version: str):
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
    yaml_payload = f"""
    datasets_version: {_version}
    datasets:
        iris:
            type: csv
            params:
                location: iris_sample_data.csv
    """

    with dataset_config_path.open('w', encoding='utf-8') as config:
        yaml.safe_dump(yaml.safe_load(yaml_payload), config)

    return path_to_csv


def test_dataset_config_init(
    dataset_csv: Path,
    project_directory: Path):
    """Basic test to see if config initialization works."""

    assert dataset_csv.exists()

    with cwd(project_directory):
        datasets = Datasets()

    assert len(datasets) == 1

def test_dataset_targets_run(dataset_csv: Path, project_directory: Path):
    assert dataset_csv.exists()

    with cwd(project_directory):
        datasets = Datasets()
        datasets.run_targets_cmd()
        assert Path('datasets', 'stores', datasets.version).exists()

PROJECT_ID = 'test-bq-project-332617'
DATASET = 'test_dataset'

@pytest.fixture
def query_script(
    project_directory: Path,
    dataset_config_path: Path,
    _version: str
    ) -> Path:

    path_to_queries_dir = Path(
        project_directory,
        'src/queries'
    )
    path_to_queries_dir.mkdir()
    src_path = Path(path_to_queries_dir, 'test-query.R')
    _query = """
    "SELECT distinct(name) as name
    FROM `bigquery-public-data.austin_bikeshare.bikeshare_stations`"
    """

    with src_path.open('w', encoding='utf-8') as file:
        file.write(_query)

    yaml_payload = f"""
    datasets_version: {_version}
    datasets:
        stations:
            type: bigquery
            params:
                table: austin_stations
                version: temp
                script: queries/test-query.R
                dataset: {DATASET}
                project_id: {PROJECT_ID}
    """

    add_datasets_yaml_payload(dataset_config_path, yaml_payload)

    return src_path


def test_query_bq_script(project_directory: Path, _version: str, query_script: Path):
    assert query_script.exists()

    with cwd(project_directory):
        datasets = Datasets()
        query_dataset = datasets['stations']

        assert isinstance(query_dataset, BigQueryDataset)
        query_dataset.perform_query()

    assert query_dataset.params.location.exists()
    assert query_dataset.exists_in_db()

    # clean up table
    query_dataset.delete_in_db()


def test_query_bq_query_expr(
    project_directory: Path,
    _version: str,
    dataset_config_path: Path):
    yaml_payload = f"""
    datasets_version: {_version}
    datasets:
        stations:
            type: bigquery
            params:
                table: austin_stations
                dataset: {DATASET}
                project_id: {PROJECT_ID}
                version: temp
                query: |
                    SELECT distinct(name) as name
                    FROM `bigquery-public-data.austin_bikeshare.bikeshare_stations`

    """

    add_datasets_yaml_payload(dataset_config_path, yaml_payload)

    with cwd(project_directory):
        datasets = Datasets()
        query_dataset = datasets['stations']

        assert isinstance(query_dataset, BigQueryDataset)
        query_dataset.perform_query()

    assert query_dataset.params.location.exists()
    assert query_dataset.exists_in_db()

    query_dataset.delete_in_db()


def test_bq_migrate(project_directory: Path, query_script: Path):
    assert query_script.exists()
    with cwd(project_directory):
        datasets = Datasets()
        query_dataset = datasets['stations']

        assert isinstance(query_dataset, BigQueryDataset)
        query_dataset.perform_query()
        query_dataset.migrate()

        assert query_dataset.params.version is not None
        assert Path(
            query_dataset.params.location,
            query_dataset.params.version).exists()















