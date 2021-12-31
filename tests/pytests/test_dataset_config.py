import pytest
from pathlib import Path
from fluke.config.datasets import Datasets
from fluke.datasets.query_dataset import BigQueryDataset
from fluke.utils import cwd
from .utils import add_datasets_yaml_payload
from tests.pytests.fixtures.datasets import PROJECT_ID, DATASET


@pytest.mark.usefixtures('dataset_csv')
def test_dataset_config_init(project_directory: Path):
    """Basic test to see if config initialization works."""
    with cwd(project_directory):
        datasets = Datasets()

    assert len(datasets) == 1

@pytest.mark.usefixtures('dataset_csv')
def test_dataset_targets_run(project_directory: Path):
    with cwd(project_directory):
        datasets = Datasets()
        datasets.run_targets_cmd()
        assert Path('datasets', '_tar_datasets_store').exists()


@pytest.mark.usefixtures('query_script')
def test_query_bq_script(project_directory: Path):

    with cwd(project_directory):
        datasets = Datasets()
        query_dataset = datasets['stations']

        assert isinstance(query_dataset, BigQueryDataset)
        query_dataset.perform_query()

    assert query_dataset.params.location.exists()
    assert query_dataset.exists_in_db()

    # clean up table
    query_dataset.delete_in_db()


def test_query_bq_query_expr(project_directory: Path, dataset_config_path: Path):
    yaml_payload = f"""
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


@pytest.mark.usefixtures('query_script')
def test_bq_migrate(project_directory: Path):
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















