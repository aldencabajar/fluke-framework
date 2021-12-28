from pathlib import Path
from typing import Callable, Generator, List, TypedDict
import pytest
import shutil
from click.testing import CliRunner
from fluke.cli.project_create import create


def pytest_configure():
    pytest.project_name = None

pytest_plugins = [
    'tests.fixtures.datasets',
]

@pytest.fixture(scope='module')
def fake_root_dir(tmp_path_factory: pytest.TempPathFactory) -> Generator:
    try:
        _dir = tmp_path_factory.mktemp('temp').resolve()
        yield _dir
    finally:
        shutil.rmtree(_dir, ignore_errors=True)

@pytest.fixture(scope='module')
def project_directory(fake_root_dir: Path) -> Path:
    project_name = 'my-test-project'
    pkg_name  = 'my_test_project'
    args = [
        '--path', str(fake_root_dir),
        '--pkg_name', pkg_name,
        project_name
    ]
    runner = CliRunner()
    result = runner.invoke(create, args)
    return Path(fake_root_dir, project_name)


@pytest.fixture(scope='session')
def cli_runner() -> CliRunner:
    runner = CliRunner()
    return runner
