import os
import json
import tempfile
import fluke
import shutil
from pathlib import Path
import click
from cookiecutter.main import cookiecutter
from distutils.dir_util import copy_tree
from fluke.core.utils import (
  get_date_and_format,
  get_cookiecutter_cfg
  )

template_dir = Path(
    Path(fluke.__file__).parent,
    'templates',
    'project'
)

config_path = get_cookiecutter_cfg(template_dir)
with config_path.open('r') as file:
    config = json.load(file)


@click.group()
def create_cli() -> None:
    pass


@create_cli.command()
@click.option("--path", "-p", "path", default=str(Path.cwd()))
@click.option("--db",  "db_type", default='bigquery')
@click.option("--pid", "project_id", required=True)
@click.option("--dataset", "dataset", required=True)
@click.argument("project_name", required=True)
def create(path: str, project_name: str,
           project_id: str, db_type: str,
           dataset: str) -> None:
    """"""

    # add needed settings to config file
    config['project_name'] = project_name
    config['db_type'] = db_type
    config['pid'] = project_id
    config['dataset'] = dataset
    config['version'] = get_date_and_format()

    # create a tempdir to copy config and relevant template files
    tmp_dir = Path(tempfile.mkdtemp(prefix='sherpa'))
    ck_dir = '{{cookiecutter.project_name}}'
    copy_tree(
        str(Path(template_dir, ck_dir)),
        str(Path(tmp_dir, ck_dir))
    )

    json_path = Path(tmp_dir, 'cookiecutter.json')
    with json_path.open('w') as f:
        json.dump(config, f)

    # use cookiecutter to transform template to dir with info
    path_to_output = os.path.expanduser(path)
    cookiecutter(str(tmp_dir), output_dir=path_to_output, no_input=True)

    # cleanup process
    shutil.rmtree(str(tmp_dir))
    click.echo(f'Created project "{project_name}" at "{path_to_output}"')

    # run project initialization
    click.echo('Initializing project using renv ...')
    os.system(f'cd {path_to_output}/{project_name};Rscript -e "renv::restore()"')

    click.echo('Finished initializing!')


if __name__ == '__main__':
    create()
