from multiprocessing.dummy.connection import Pipe
from shutil import ExecError
from subprocess import PIPE
from typing_extensions import TypedDict
from typing import TYPE_CHECKING, Any, Dict
import pytest
from pathlib import Path
from click.testing import CliRunner, Result
from fluke.cli.pipeline import pipeline

PIPELINE_NAME = 'test_pipeline'

class PipelineFixtureParam(TypedDict):
    scripts: Dict[Path, str]


if TYPE_CHECKING:
    class FixtureRequest:
        param: PipelineFixtureParam
else:
    from pytest import FixtureRequest


@pytest.fixture
def pipeline_fixture(cli: CliRunner, request: FixtureRequest) -> Result:
    results = cli.invoke(pipeline, ['create', PIPELINE_NAME], echo=True)
    try:
        if request.param is not None:
            for path, src in request.param['scripts'].items():
                script_path = Path('pipelines', PIPELINE_NAME, path)
                with script_path.open('a', encoding='utf-8') as file:
                    file.write(src)
    finally:
        return results


def test_pipeline_create(pipeline_fixture: Result, project_directory: Path) -> None:
    assert pipeline_fixture.exit_code == 0
    pipeline_path = Path(project_directory, 'pipelines', PIPELINE_NAME)
    assert pipeline_path.exists()

TEST_SCRIPT = """
list(
    tar_target(data1, data.frame(a = c(1,2), b= c(3,4))),
    tar_target(proc, data1$a + 1)
)
"""
@pytest.mark.parametrize("pipeline_fixture",
[PipelineFixtureParam(scripts={Path('pipeline.R'): TEST_SCRIPT}), ],
indirect=True)
def test_pipeline_run_all(cli: CliRunner, pipeline_fixture: Result):
    results = cli.invoke(pipeline, ['run'])


