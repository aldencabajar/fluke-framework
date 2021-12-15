from pathlib import Path
from typing import List, Optional, Dict, TypedDict
import fluke
import click
from fluke.core.config import Config
from fluke.core.objects.table import TableVersion
from fluke.core.utils import sym_wrap, run_r
from fluke.core.objects import SherpaObject, Dataset

# Find path for necessary R functions
r_dir = Path(Path(fluke.__file__).parent.parent, 'R')
query_funcs = Path(r_dir, 'query_utils.R')
migrate_funcs = Path(r_dir, 'migrate_utils.R')

class DatabaseInfo(TypedDict):
    type: str
    migrate_fn: str
    params: Dict[str, Optional[str]]


class DatabaseStruct(TypedDict):
    query_fn: str
    migrate_fn: str
    param_struct: Dict[str, Optional[str]]


class Database(Config, SherpaObject):
    """Database representation"""
    param_struct: Dict[str, Optional[str]]
    migrate_fn: str
    query_fn: str

    def __init__(self, info: DatabaseInfo) -> None:

        self.type = info['type']
        self.params = info['params']
        # overwrites the default
        self.migrate_fn =  info['migrate_fn']
        self._check_params()

    @classmethod
    def set_param_struct(cls, db_struct: DatabaseStruct) -> None:
        """Sets the database structure to describe the type of database."""
        cls.param_struct = db_struct['param_struct']
        cls.migrate_fn = db_struct['migrate_fn']
        cls.query_fn = db_struct['query_fn']

    def _check_params(self):
        for k, _ in self.param_struct.items():
            try:
                self.params[k]
            except Exception as no_param_exist:
                raise Exception(
                    f'`{k}` does not exist in params provided in project-config.yml'
                ) from no_param_exist


    def r_argument(self) -> List[str]:
        named_args = []
        for arg_name, value in self.params.items():
            if value is None:
                value = 'NULL'
            named_args.append(
                arg_name + '=' + sym_wrap(value, '\'')
            )
        return named_args

    def query(self, tbl_ver: TableVersion) -> None:
        """Using R src  path and table name, query a database."""

        wrapped_path = sym_wrap(str(tbl_ver.get_path()), "'")
        query_fn_arg = f'query_fn = {self.query_fn}'
        param_args = self.r_argument()
        tbl_arg = 'table=' + sym_wrap(tbl_ver.cat_table_version(), '\'')
        all_args = ', '.join([wrapped_path, query_fn_arg, *param_args, tbl_arg])

        # structuring the command string
        source_expr = 'source(%s)' % (sym_wrap(str(query_funcs), '\''))
        cmd = f'query_run_wrapper({all_args})'
        all = ';'.join([source_expr, cmd])

        run_r(all, ['-e'])

    def to_write(self):
        ...

    def set_version(self):
        raise NotImplementedError

    def migrate(self, dataset: Dataset,  tbl_version: TableVersion) -> None:
        """Migrate a table to a local data cache from a database."""
        dataset.add(tbl_version)
        source_expr = 'source(%s)' % (
            sym_wrap(str(migrate_funcs), '\'')
        )
        tbl_arg = 'table = %s' % (sym_wrap(tbl_version.cat_table_version()))
        param_args = self.r_argument()
        ds_dir = f'dataset_dir = {sym_wrap(dataset.name)}'
        migrate_fn_arg =  f'migrate_fn = {self.migrate_fn}'
        all_args = ', '.join([ds_dir, migrate_fn_arg, tbl_arg, *param_args])
        cmd = f'migrate_run_wrapper({all_args})'
        all =  ';'.join([source_expr, cmd])

        run_r(all, ['-e'])
        click.echo(
            (f'Successfully migrated table `{tbl_version.name}`'
            f' with version `{tbl_version.version}` to `{dataset.path_to_dataset}`')
        )


def get_database_cls(info: DatabaseInfo) -> Database:
    """Factory function for Database Classes"""
    db_param_map: Dict[str, DatabaseStruct] = {
        'bigquery': {
            'migrate_fn': 'migrate_bigquery',
            'query_fn':  'bigquery_query_fn',
            'param_struct': {
                'dataset': None,
                'project': None
            }
        }
    }
    try:
        Database.set_param_struct(db_param_map[info['type']])
        return Database(info)
    except NotImplementedError as not_implemented:
        raise NotImplementedError(
            ('Database type `%s` not yet implemented.') % (info['type'])
        ) from not_implemented
