from dataclasses import dataclass
from multiprocessing.dummy.connection import Pipe
from shutil import ExecError
from subprocess import PIPE
from typing_extensions import TypedDict
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import pytest
import yaml
from pathlib import Path
from click.testing import CliRunner, Result
from fluke.cli.pipeline import pipeline
from pytest import FixtureRequest

PIPELINES_VERSION = 'TEST_PIPELINE_VERSION'
PIPELINE_NAME = 'test_pipeline'
TEST_SCRIPT = """
list(
    tar_target(data1, data.frame(a = c(1,2), b= c(3,4))),
    tar_target(proc, data1$a + 1)
)
"""

@dataclass
class PipelineFixtureParam:
    name: str
    scripts: Optional[Dict[Path, str]] = None


class PipelineFixtureRequest(FixtureRequest):
    param: PipelineFixtureParam


class PipelinesConfigRequest(FixtureRequest):
    param: Dict[str, str]

@pytest.fixture(scope='module', autouse=True)
def pipelines_config(project_directory: Path) -> None:
    params  = {'pipelines': {'version': PIPELINES_VERSION}}
    _ppl_config_path = Path(project_directory, 'config', 'pipelines.yaml')
    with _ppl_config_path.open('w', encoding='utf-8') as file:
        _config = yaml.safe_dump(params, file)


@pytest.fixture
def pipeline_fixture(cli: CliRunner, request: PipelineFixtureRequest) -> Result:
    results = cli.invoke(pipeline, ['create', request.param.name], echo=True)
    assert request.param.scripts is not None
    for path, src in request.param.scripts.items():
        script_path = Path('pipelines', request.param.name, path)
        with script_path.open('a', encoding='utf-8') as file:
            file.write(src)
    return results


@pytest.mark.parametrize('pipeline_fixture',
[PipelineFixtureParam(name=PIPELINE_NAME, scripts={Path('pipeline.R') : TEST_SCRIPT}), ], indirect=True)
def test_pipeline_create(pipeline_fixture: Result, project_directory: Path) -> None:
    assert pipeline_fixture.exit_code == 0
    pipeline_path = Path(project_directory, 'pipelines', PIPELINE_NAME)
    assert pipeline_path.exists()

@pytest.mark.parametrize("pipeline_fixture",
[PipelineFixtureParam(name=PIPELINE_NAME, scripts={Path('pipeline.R'): TEST_SCRIPT}), ],
indirect=True)
def test_pipeline_run_all(cli: CliRunner, pipeline_fixture: Result):
    results = cli.invoke(pipeline, ['run'])
    assert results.exit_code == 0

class MultPipelineFixtureRequest(FixtureRequest):
    param: List[PipelineFixtureParam]

@pytest.fixture
def multiple_pipelines_fixture(cli: CliRunner,
request: MultPipelineFixtureRequest) -> List[Result]:
    result_list = []
    for ppl in request.param:
        results = cli.invoke(pipeline, ['create', ppl.name], echo=True)
        result_list.append(results)
        assert ppl.scripts is not None
        for path, src in ppl.scripts.items():
            script_path = Path('pipelines', ppl.name, path)
            with script_path.open('a', encoding='utf-8') as file:
                file.write(src)
    return result_list

TEST_SCRIPT_2 = """
    list(
        tar_target(proc2, proc * 5),
        tar_target(proc3, as.character(proc2))
    )
"""

MULTIPLE_PIPELINES = [
    PipelineFixtureParam(
        name = 'pipeline_1',
        scripts = {Path('pipeline.R') : TEST_SCRIPT}
    ),
    PipelineFixtureParam(
        name = 'pipeline_2',
        scripts = {Path('pipeline.R'): TEST_SCRIPT_2}
    )
]

@pytest.mark.parametrize("multiple_pipelines_fixture",
[MULTIPLE_PIPELINES, ], indirect=True)
def test_single_pipeline_run(cli: CliRunner, multiple_pipelines_fixture: List[Result]):
    results = cli.invoke(pipeline, ['run', '--name', 'pipeline_1'])
    assert results.exit_code == 0

    # detect if objects from pipeline_1 are in targets store
    store = Path('pipelines', 'store', PIPELINES_VERSION, 'objects')
    _objects = ['data1', 'proc']
    files = [
        _file.name for _file in store.iterdir() if _file.name in _objects
    ]
    assert len(files) == len(_objects)









