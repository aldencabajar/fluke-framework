from pathlib import Path
from typing import Generator, Optional, TypedDict
from click.core import Option
import pytest
import shutil
from click.testing import CliRunner
from fluke.cli.project_create import create


def pytest_configure():
    pytest.project_name = None

@pytest.fixture
def fake_root_dir(tmp_path) -> Generator:
    try:
        yield Path(tmp_path).resolve()
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)

@pytest.fixture
def project_directory(fake_root_dir: Path) -> Path:
    project_name = 'my-test-project'
    pkg_name  = 'my_test_project'
    args = [
        '--path', fake_root_dir,
        '--pkg_name', pkg_name,
        project_name
    ]
    runner = CliRunner()
    result = runner.invoke(create, args)
    return Path(fake_root_dir, project_name)