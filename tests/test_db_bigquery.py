# from pathlib import Path
# from typing import Generator
# from click.testing import CliRunner
# import pytest
# from sherpa.cli.query_tables import query
# from .utils import cwd

# TBL_NAME = 'distinct_station_ids'
# QUERY_SCRIPT = """
# 'SELECT DISTINCT(name) as name
# FROM `bigquery-public-data.austin_bikeshare.bikeshare_stations`'
# """

# @pytest.fixture
# def test_script(project_directory: Path, request) -> Path:
#     script_path = Path(
#         project_directory,
#         'src/data_pull',
#         f'create_{request.param}.R')

#     return script_path

# @pytest.mark.parametrize('test_script', [TBL_NAME], indirect=True)
# def test_query_table(test_script: Path, project_directory: Path):
#     """
#     simple testing for querying tables.
#     """
#     # writing query string to script.
#     with test_script.open('w', encoding='utf-8') as file:
#         file.write(QUERY_SCRIPT)

#     args = [TBL_NAME]
#     runner = CliRunner()
#     with cwd(Path(project_directory)):
#         results = runner.invoke(query, args)
#     assert results.exception is None





