import pytest
from pathlib import Path
from click.testing import CliRunner
from fluke.cli.pipeline import pipeline

PIPELINE_NAME = 'test_pipeline'

def test_pipeline_create(cli: CliRunner, project_directory: Path) -> None:
    args = ['create', PIPELINE_NAME]
    results = cli.invoke(pipeline, args, echo=True)
    print(results)
    assert results.exit_code == 0
    pipeline_path = Path(project_directory, 'pipelines', PIPELINE_NAME)

    assert pipeline_path.exists()

