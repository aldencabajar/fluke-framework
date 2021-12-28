from typing import Dict, Generator, List
from typing_extensions import TypedDict
import pytest
import shutil
from pathlib import Path
from tests.utils import add_datasets_yaml_payload
from fluke.core.utils import cwd, run_r

PROJECT_ID = 'test-bq-project-332617'
DATASET = 'test_dataset'


@pytest.fixture
def dataset_config_path(project_directory: Path) -> Path:
    return Path(project_directory, 'config', 'datasets.yaml')

@pytest.fixture
def dataset_csv(project_directory: Path,
    dataset_config_path: Path):
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
    datasets:
        iris:
            type: csv
            params:
                location: iris_sample_data.csv
    """

    add_datasets_yaml_payload(dataset_config_path, yaml_payload)

    return path_to_csv

@pytest.fixture
def query_script(project_directory: Path, dataset_config_path: Path) -> Generator:
    try:
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
        yield src_path
    finally:
        shutil.rmtree(path_to_queries_dir)


@pytest.fixture
def yaml_payload():
    yml = f"""
    bq_settings: &bq
        dataset: {DATASET}
        project_id: {PROJECT_ID}
    datasets:
        stations:
            type: bigquery
            params:
                <<: *bq
                table: austin_stations
                version: temp
                query: |
                    select distinct(name) as name
                    FROM `bigquery-public-data.austin_bikeshare.bikeshare_stations`
        address:
            type: bigquery
            params:
                <<: *bq
                table: address
                version: '20211228'
                query: |
                    select distinct(address) as add
                    FROM `bigquery-public-data.austin_crime.crime`

    """
    return yml


@pytest.fixture
def multiple_queries(dataset_config_path: Path, yaml_payload: str):
    add_datasets_yaml_payload(dataset_config_path, yaml_payload)
