from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, Union
from fluke.utils import (
    dict_to_r_args,
    find_root_proj,
    run_r,
    tar_cmd_generator,
    dict_insert,
    sym_wrap
)
from fluke.datasets.query_dataset import QueryParams, QueryDataset
from fluke.logger import init_logger

logger = init_logger()

@dataclass
class BigQueryParams(QueryParams):
    project_id: Optional[str] = None
    dataset: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._location = Path(
            find_root_proj(),
            'datasets',
            f'{self.project_id}.{self.dataset}.{self.table}'
        )

    @property
    def location(self) -> Path:
        return self._location

    def _check_params(self) -> None:
        super()._check_params()
        required_attrs = ['project_id', 'dataset']
        missing = []
        for _attr in required_attrs:
            if getattr(self, _attr) is None:
                missing.append(_attr)
        if len(missing) > 0:
            missing_cat = ', '.join([f'`{m}`' for m in missing])
            raise Exception(f'Args {missing_cat} are missing for `BigQueryDataset`.')


class BigQueryDataset(QueryDataset):
    @property
    def _param_struct(self) -> Type[BigQueryParams]:
        return BigQueryParams

    @property
    def params(self) -> BigQueryParams:
        return self._params

    @property
    def bq_table(self) -> str:
        """a `bigrquery` representation of a bigquery table."""
        p = self.params
        tbl = f"""
        bigrquery::bq_table(
            "{p.project_id}",
            "{p.dataset}",
            "{p.ver_tbl}"
        )
        """
        return tbl

    def __init__(self, name: str, params: Dict[str, Optional[Any]]) -> None:
        super().__init__(name, params)

    def _set_params(self, params: Dict[str, Optional[Any]]) -> None:
        self._params = self._param_struct(**params)

    def tar_cmd(self) -> str:
        if self.params.read_fun_args is not None:
            _fnl_args = dict_insert(
                self.params.read_fun_args, 0,
                str(self.params.location))
        else:
            _fnl_args = {'': str(self.params.location)}

        _read_fun_args = dict_to_r_args(_fnl_args)

        cmd = tar_cmd_generator(
            self.name,
            fun = self.params.read_fun,
            fun_args = _read_fun_args
        )

        return cmd

    def perform_query(self) -> None:
        super().perform_query()
        p = self.params
        cmd = f"""
        tbl <- {self.bq_table}

        {p.query_str}
        bigrquery::bq_project_query(
            "{p.project_id}",
             query = query,
            destination_table = tbl,
            write_disposition = "WRITE_TRUNCATE"
        )
        """
        run_r(cmd, ['-e'], quiet = True)
        logger.info(
            (f'Created table {self.params.ver_tbl} in '
            f'{self.params.project_id}.{self.params.dataset}.'
            )
        )

    def migrate(self) -> None:
        p = self.params
        # prepare migration args
        migrate_args_r: List[Union[str, None]]
        if p.migrate_fun_args is not None:
            migrate_args_r = []
            for __kt, __vt in dict_to_r_args(p.migrate_fun_args).items():
                migrate_args_r.append(f'{__kt} = {__vt}')
        else:
            migrate_args_r = [None]

        if p.migrate_fun == 'bigrquery::bq_table_download':
            migrate_args_r.insert(0, self.bq_table)
            all_args = list(
                filter(None, migrate_args_r)
            )
            all_args_expr = ','.join(all_args)

        else:
            if p.table is not None:
                migrate_args_r.insert(0, sym_wrap(p.table))

        if p.version is not None:
            file_path = Path(p.location, p.version)

        cmd = f"""
            downloaded <- {p.migrate_fun}({all_args_expr})
            saveRDS(downloaded, "{file_path}")
        """

        run_r(cmd, ['-e'], quiet= True)
        logger.info(
            (f'Migrated {p.project_id}.{p.dataset}.{p.ver_tbl} to datasets/.')
        )

    def exists_in_db(self) -> bool:
        cmd = f"""
        tbl <- {self.bq_table}
        bigrquery::bq_table_exists(tbl)
        """
        result = run_r(cmd, ['-e'], quiet=True)

        return 'TRUE' in result

    def delete_in_db(self) -> None:
        cmd=f"""
        tbl <- {self.bq_table}
        bigrquery::bq_table_delete(tbl)
        """
        run_r(cmd, ['-e'], quiet=True)
        logger.info(
            (f'Deleted table {self.params.ver_tbl} in '
            f'{self.params.project_id}.{self.params.dataset}.'
            )
        )
