from pathlib import Path
from copy import copy
from typing import Any, Dict, List, Mapping, Optional, Type, TypedDict, Union
import yaml
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from fluke.core.utils import (
    dict_to_r_args,
    find_root_proj,
    run_r,
    tar_cmd_generator,
    dict_insert,
    sym_wrap
)


class AbstractParam(ABC):
    @abstractmethod
    def _check_params(self) -> None:
        ...


class AbstractDataset(ABC):
    @abstractmethod
    def __init__(self, name: str, params: Dict[str, Optional[Any]]) -> None:
        self.name = name
        self._set_params(params)

    @abstractmethod
    def tar_cmd(self) -> str:
        """abstract method to construct command for `targets`."""
        ...

    @abstractmethod
    def _set_params(self, params: Dict[str, Optional[Any]]) -> None:
        """abstract method to set params for instance."""
        ...

    @property
    @abstractmethod
    def _param_struct(self) -> Type[AbstractParam]:
        ...

    @property
    @abstractmethod
    def params(self) -> AbstractParam:
        ...


@dataclass
class CSVParams(AbstractParam):
    location: Optional[Path]
    read_fun: Optional[str] = 'read.csv'
    read_fun_args: Optional[Dict[str, Optional[Any]]] = None

    def __post_init__(self):
        self._check_params()
        self.location = Path(find_root_proj(), 'datasets', self.location)

    def _check_params(self):
        if self.location is None:
            raise Exception('`location` argument must be provided.')

        if self.read_fun is None:
            raise Exception('`read_fun` argument must be provided.')


class CSVDataset(AbstractDataset):
    """Dataset class for csv"""
    @property
    def _param_struct(self) -> Type[CSVParams]:
        return CSVParams

    @property
    def params(self) -> CSVParams:
        return self._params

    def __init__(self, name: str, params: Dict[str, Optional[Any]]) -> None:
        super().__init__(name, params)

    def _set_params(self, params: Dict[str, Optional[Any]]) -> None:
        _params = self._param_struct(**params)
        self._params = _params


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


@dataclass
class QueryParams(AbstractParam):
    script: Optional[str] = None
    query: Optional[str] = None
    version: Optional[str] = ''
    table: Optional[str] = None
    migrate_fun: Optional[str] = 'bigrquery::bq_table_download'
    read_fun: Optional[str] = 'readRDS'
    migrate_fun_args: Optional[Dict[str, Optional[Any]]] = None
    read_fun_args: Optional[Dict[str, Optional[Any]]] = None

    def __post_init__(self):
        self._check_params()
        self.ver_tbl = '_'.join([self.table, self.version])

        # derive the real path for the script
        src_path: Optional[Path]
        if self.script is not None:
            src_path = Path(find_root_proj(), 'src', self.script)
        else:
            src_path = None
        self.src_path = src_path

        # derive the query to be used
        if self.script is not None:
            _query = f"""
            env <- new.env()
            query <- source('{self.src_path}', local = env)$value
            """
        else:
            _query = f'query <- "{self.query}"'
        self.query_str = _query

    @property
    @abstractmethod
    def location(self) -> Path:
        ...

    def _check_params(self):
        if self.script is None and self.query is None:
            raise Exception(
                ('Node `script` or `query` must be'
                ' included in `datasets.yaml` if `query_dataset` is '
                'declared.')
            )

        if self.script is not None and self.query is not None:
            raise Exception(
                ('Defining both `script` and `query` is invalid.')
            )

        if self.table is None:
            raise Exception('`table` must be provided!')


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


class QueryDataset(AbstractDataset):
    @property
    @abstractmethod
    def _param_struct(self) -> Type[QueryParams]:
        ...

    @property
    @abstractmethod
    def params(self) -> QueryParams:
        ...

    @abstractmethod
    def perform_query(self) -> None:
        p = self.params
        # check if the script exists
        if p.script is not None:
            self._check_script_exists()

        # create dataset location if it does not exist.
        with p.location as loc:
            if not loc.exists():
                loc.mkdir()

    @abstractmethod
    def migrate(self):
        ...

    @abstractmethod
    def exists_in_db(self) -> bool:
        ...

    @abstractmethod
    def delete_in_db(self) -> None:
        """deletes a table version."""
        ...

    def _check_script_exists(self):
        if not self.params.src_path.exists():
            raise Exception(
                f'The query script {self.params.script} does not exist!'
            )


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

        run_r(cmd, ['-e'])

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

        run_r(cmd, ['-e'])



    def exists_in_db(self) -> bool:
        cmd = f"""
        tbl <- {self.bq_table}
        bigrquery::bq_table_exists(tbl)
        """
        result = run_r(cmd, ['-e'])

        return 'TRUE' in result

    def delete_in_db(self) -> None:
        cmd=f"""
        tbl <- {self.bq_table}
        bigrquery::bq_table_delete(tbl)
        """
        run_r(cmd, ['-e'])


def dataset_class_factory(
    dataset_type: str,
    name: str,
    params: Dict[str, Optional[Any]]
    ) -> AbstractDataset:
    """
    generates an instantiated Dataset Class from name and params.
    """

    datasets: Dict[str, Type[AbstractDataset]] = {
        'csv' : CSVDataset,
        'bigquery': BigQueryDataset
    }

    dataset_object = datasets[dataset_type](name, params)

    return dataset_object



class DatasetConfig(TypedDict):
    type: str
    params: Dict[str, Optional[Any]]

class DatasetsYAMLConfig(TypedDict):
    datasets: Dict[str, DatasetConfig]

class Datasets(dict):
    """Class to be instantiated to encapsulate datasets info."""
    def __init__(self):
        datasets_yaml_config: DatasetsYAMLConfig
        ds_config: Dict[str, DatasetConfig]
        self.ds_config_path = Path(find_root_proj(), 'config', 'datasets.yaml')
        with self.ds_config_path.open('r', encoding='utf-8') as cfg:
            try:
                datasets_yaml_config = yaml.safe_load(cfg)
                ds_config =  datasets_yaml_config['datasets']
            except KeyError as error:
                print('datasets.yaml does not contain `datasets` node.')
        self.ds_config = ds_config

        _list: List[AbstractDataset] = []
        for name, values in self.ds_config.items():
            _dataset_obj = dataset_class_factory(values['type'], name, values['params'])
            _list.append(_dataset_obj)
        self._list = _list

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self) -> AbstractDataset:
        if self._index < len(self._list):
            out = self._list[self._index]
            self._index += 1
            return out
        else:
            raise StopIteration


    def __getitem__(self, __k: str) -> AbstractDataset:
        try:
            for dataset in self._list:
                if dataset.name == __k:
                    _ds = dataset
            return _ds
        except Exception as error:
            raise KeyError(
                f'Dataset `{__k}` does not exist!'
            ) from error

    def __len__(self) -> int:
        return len(self._list)

    def query_dataset_exists(self) -> bool:
        query_ds_cnt = 0
        for _dataset in self._list:
            if isinstance(_dataset, QueryDataset):
                query_ds_cnt += 1
        return query_ds_cnt > 0


    def run_targets_cmd(self) -> None:
        """
        generates a `targets` package list of targets
        from dataset list.
        """
        _tar_list = ',\n'.join(
            [dataset.tar_cmd() for dataset in self._list]
        )
        _tar_cmd = f"""
        library(targets)
        Sys.setenv(TAR_CONFIG = here::here('config/_targets.yaml'))
        Sys.setenv(TAR_PROJECT = 'datasets')

        tar_config_set(
            store = 'datasets/_tar_datasets_store',
            script = 'datasets/tar_script_datasets.R'
        )

        tar_script({{
            # Encapsulates `targets` commands for datasets.
            # Do not edit by hand!
            list(
                {_tar_list}
            )
        }})

        tar_make()
        """
        run_r(_tar_cmd, ['-e'])

        return




