from pathlib import Path
import pytest

def test_simple_create(project_directory: Path) -> None:
    assert project_directory.exists()

def test_pkgname_checks_valid(fake_root_dir: Path) -> None:
    ...