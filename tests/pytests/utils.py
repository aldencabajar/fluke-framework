import os
import yaml
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def cwd(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

def add_datasets_yaml_payload(
    dataset_config_path: Path,
    yaml_payload: str) -> None:

    with dataset_config_path.open('w', encoding='utf-8') as config:
        yaml.safe_dump(
            yaml.safe_load(yaml_payload),
            config)
    return
