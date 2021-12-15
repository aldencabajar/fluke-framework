import shutil
from pathlib import Path
from typing import List
import click
import fluke
from fluke.core.utils import (
    find_root_proj,
    _create_dir_using_cookiecutter,
    run_r,
    sym_wrap
)


class PipelineDependencies:
    """Defines the directories and dependencies needed for pipelines."""
    def __init__(self):
        self.template_dir = Path(
            Path(fluke.__file__).parent,
            'templates',
            'pipeline',
            '{{cookiecutter.pipeline_name}}'
        )
        self.project_pipeline_dir = Path(find_root_proj(), 'pipelines')
        self.targets_yaml_path = Path(self.project_pipeline_dir, '_targets.yaml')


def get_pipelines() -> List[Path]:
    ppl_path = Path(find_root_proj(), 'pipelines')
    pipelines = []
    for _dir in ppl_path.iterdir():
        if _dir.is_dir():
            # detect if pipeline yml and main.R exists
            ppl_yml = Path(_dir, 'pipeline.yml')
            main_r_script = Path(_dir, 'main.R')
            if ppl_yml.exists() and main_r_script.exists():
                pipelines.append(_dir)
    return pipelines


@click.group(invoke_without_command=True)
@click.option('--list', 'list_pipelines', is_flag=True)
@click.pass_context
def pipeline(ctx: click.Context, list_pipelines: bool) -> None:
    """
    Command-line interface for pipelines.
    """
    deps = PipelineDependencies()
    ppl = get_pipelines()
    ctx.obj = deps
    if list_pipelines:
        for pp in ppl:
            click.echo(pp.name)

@pipeline.command('create')
@click.argument('name', required=True)
@click.pass_obj
def create(deps: PipelineDependencies, name: str) -> None:
    _config = {'pipeline_name': name}
    path_to_pipeline = Path(deps.project_pipeline_dir, name)
    if path_to_pipeline.exists():
        if click.confirm((
            'This will delete the pipeline folder'
             ' with the existing name. Continue?')
        ):
            shutil.rmtree(path_to_pipeline)
        else:
            return

    _create_dir_using_cookiecutter(
        deps.template_dir,
        deps.project_pipeline_dir,
        _config
    )
    # set config in _targets.yaml
    targets_store = Path(deps.project_pipeline_dir, name, '_targets_store')
    main_src_path = Path(deps.project_pipeline_dir, name, 'main.R')
    targets_pkg_set = f"""
    targets::tar_config_set(
        script = {sym_wrap(str(main_src_path))},
        store =  {sym_wrap(str(targets_store))},
        config = {sym_wrap(str(deps.targets_yaml_path))},
        project = {sym_wrap(name)}
    )
    """
    run_r(targets_pkg_set, ['-e'])
    click.echo((
        f'\ncreated `{str(path_to_pipeline)}`'
        f'\n add pipeline `{name}` to {str(deps.targets_yaml_path)}\n'
    ))



def get_pipeline_names_click(ctx, args, incomplete):
    """Find create_* scripts and pass as suggestions when query."""
    ppl_path_str = [str(pp.name) for pp in get_pipelines()]
    return [k for k in ppl_path_str if k.startswith(incomplete)]

@pipeline.command('run')
@click.option('--workers', type=int, default=1, required=False)
@click.argument('name', required=True, shell_complete = get_pipeline_names_click)
@click.pass_obj
def run(deps: PipelineDependencies, name: str, workers: int) -> None:
    """Run the `targets` make for pipeline."""

    if not Path(deps.project_pipeline_dir, name).exists():
        raise Exception(
            (f'Pipeline `{name}` does not exist. '
            'Consider creating one using `pipeline create.`')
        )

    if workers > 1:
        tar_make_cmd = 'targets::tar_make_future()'
    else:
        tar_make_cmd = 'targets::tar_make()'

    run_cmd = f"""
    Sys.setenv(TAR_PROJECT = {sym_wrap(name)})
    Sys.setenv(TAR_CONFIG = {sym_wrap(str(deps.targets_yaml_path))})
    {tar_make_cmd}
    """
    run_r(run_cmd, ['-e'])
