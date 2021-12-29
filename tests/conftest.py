import os
from pathlib import Path
from typing import Callable, Generator, List, TypedDict
import sys
import pytest
from pytest import TempPathFactory
import functools
import shutil
from click.testing import CliRunner
from fluke.cli.project_create import create

PROJECT_NAME = 'my-test-project'
PKG_NAME = 'my_test_project'

def pytest_configure():
    pytest.project_name = None

pytest_plugins = [
    'tests.fixtures.datasets',
]


@pytest.fixture(scope='module', autouse=True)
def project_directory(tmp_path_factory: TempPathFactory) -> Generator[Path, None, None]:
    try:
        owd = os.getcwd()
        _dir = tmp_path_factory.mktemp('temp').resolve()
        args = [
            '--path', str(_dir),
            '--pkg_name', PKG_NAME,
            PROJECT_NAME
        ]
        runner = CliRunner()
        runner.invoke(create, args)
        path_to_proj = Path(_dir, PROJECT_NAME)
        os.chdir(path_to_proj)
        yield path_to_proj
    finally:
        shutil.rmtree(_dir, ignore_errors=True)
        os.chdir(owd)


@pytest.fixture(scope='session')
def cli_runner() -> CliRunner:
    runner = CliRunner()
    return runner

@pytest.fixture(scope='session')
def cli():
    """Yield a click.testing.CliRunner to invoke the CLI."""
    class_ = CliRunner

    def invoke_wrapper(f):
        """Augment CliRunner.invoke to emit its output to stdout.

        This enables pytest to show the output in its logs on test
        failures.

        """
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            echo = kwargs.pop('echo', False)
            result = f(*args, **kwargs)

            if echo is True:
                sys.stdout.write(result.output)

            return result

        return wrapper

    class_.invoke = invoke_wrapper(class_.invoke)
    cli_runner = class_()

    yield cli_runner
