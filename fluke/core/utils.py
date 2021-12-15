from datetime import datetime
from distutils.dir_util import copy_tree
import json
from pathlib import Path
import tempfile
from typing import List, Dict
from copy import copy
import os
import re
import shutil
import subprocess
import click
from cookiecutter.main  import cookiecutter


def get_r_version() -> None:
    """determine the R version and print it."""
    return None


def get_date_and_format() -> str:
    """get current date and format it."""
    _date = datetime.now()
    return _date.strftime("%Y%m%d")


def get_cookiecutter_cfg(dir: Path) -> Path:
    return Path(dir, 'cookiecutter.json')


def find_root_proj() -> Path:
    """
    Find the root project path starting from current directory
    """
    curr_path = Path.cwd()
    while 'sherpa-config.json' not in os.listdir(curr_path):
        prev_path = copy(curr_path)
        curr_path = prev_path.parent
        if curr_path == prev_path:
            raise click.UsageError((
                'Cannot find \'sherpa-config.json\'. '
                'you must be inside a sherpa project dir.')
            )

    return curr_path.resolve()




def _is_rscript(file: Path) -> bool:
    """detects if a file is an Rscript"""
    r_pattern = re.compile(r'.*(\.R|\.r)$')
    return bool(r_pattern.match(file.name))


def run_r(src: str, flags: List[str] = None) -> None:
    """runs an Rscript command
    Args:
    src: Script path or command (commands need to be double quoted)
    """
    concat_flags = ' '.join(flags) if flags is not None else ''
    try:
        # subprocess.run(f'Rscript {concat_flags} {src}', check=True)
        subprocess.run(['Rscript', *flags, src], check=True)
    except subprocess.CalledProcessError as err:
        raise Exception('There seems to be a problem in the query!')



def sym_wrap(string: str, sym: str = '\'') -> str:
    """wraps a string with symbols."""
    return f'{sym}{string}{sym}'


def _find_create_scripts(proj_root: Path) -> List[Path]:
    """
        Find scripts that start with 'create_' under 'data_pull/src'
    """
    DATA_PULL_PATH = Path.joinpath(proj_root, 'src/data_pull')
    r_scripts = [
        s for s in DATA_PULL_PATH.iterdir()
        if _is_rscript(s)
    ]
    # identify scripts starting with "create__"
    create_ptr = re.compile(r'^create_.*\.(R|r)$')
    create_scripts = [
        s for s in r_scripts
        if bool(create_ptr.match(s.name))
    ]
    return create_scripts


def _get_table_names(scripts: List[Path]) -> Dict[str, Path]:
    """extracts table names from create_scripts
    Arguments:
    scripts -  List of scripts from `_find_create_scripts`
    """
    # extract table name after "create_"
    ptr = re.compile(r'^create_(.*)')
    table_names = [
        ptr.search(s.stem).group(1)
        for s in scripts
    ]

    table_names_map = dict([
        (k, v.resolve())
        for k, v in zip(table_names, scripts)
    ])

    return table_names_map


def _create_dir_using_cookiecutter(
    template_dir: Path, dest_dir: Path,
    config: Dict[str, str]
    ) -> None:
    """
    Using templates from the main package, create a temporary
    directory to transform it using cookiecutter from
    `cookiecutter.json` config.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix='sherpa'))
    copy_tree(
        str(template_dir),
        str(Path(temp_dir, template_dir.name))
    )
    json_path = Path(temp_dir, 'cookiecutter.json')
    with json_path.open('w') as jsonfile:
        json.dump(config, jsonfile)

    # create directory using cookiecutter
    cookiecutter(
        str(temp_dir),
        output_dir=dest_dir,
        no_input=True
    )
    # cleanup process
    shutil.rmtree(str(temp_dir))


def get_table_names_click(ctx, args, incomplete):
    """Find create_* scripts and pass as suggestions when query."""
    proj_root = find_root_proj()
    create_scripts = _find_create_scripts(proj_root)
    src_table_map = _get_table_names(create_scripts)
    return [k for k in src_table_map if k.startswith(incomplete)]


class RemoveRequire(click.Argument):
    """Class for changing require flag
    given the presence of another parameter."""
    def __init__(self, *args, **kwargs):
        self.remove_req_if = kwargs.pop('remove_req_if')
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        remove_in_opts = self.remove_req_if in opts
        arg_not_none = not opts[self.name] is None

        if arg_not_none:
            if remove_in_opts:
                raise click.UsageError(
                        "Illegal usage: `%s` is mutually exclusive with `%s`"
                        % ('TABLE', '--all'))
        elif not arg_not_none and not remove_in_opts:
            self.required = True

        return super().handle_parse_result(ctx, opts, args)

class RemoveRequireOpt(click.Option):
    """Option class version for RemoveRequire"""
    def __init__(self, *args, **kwargs):
        self.remove_req_if = kwargs.pop('remove_req_if')
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        remove_in_opts = self.remove_req_if in opts
        name_in_opts = self.name in opts

        if remove_in_opts:
            if name_in_opts:
                raise click.UsageError(
                        "Illegal usage: `%s` is mutually exclusive with `%s`"
                        % ('TABLE', '--all'))
            else:
                self.required = False

        return super().handle_parse_result(ctx, opts, args)


class Cadence:
    cadence_options = ['day', 'week', 'month']

    def __init__(self, kw: str):
        self.kw = kw
        if not self.is_opt_implemented():
            raise NotImplementedError(
                ('cadence `%s` not yet implemented. Please choose among %s.')
                % (self.kw, ', '.join(self.cadence_options))
            )

    def is_opt_implemented(self) -> bool:
        return self.kw in self.cadence_options

    def version(self) -> str:
        datenow = datetime.now()
        frmt ={
            'day': datenow.strftime('%Y%m%d'),
            'month': datenow.strftime('%Y%m'),
            'week': datenow.strftime('%Y%m%d')
        }
        return frmt[self.kw]
