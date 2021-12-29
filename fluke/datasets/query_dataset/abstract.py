"""Abstract classes for QueryDatasets."""
from pathlib import Path
from dataclasses import dataclass
from fluke.datasets.abstract import AbstractDataset, AbstractParam
from typing import Any, Dict, Optional, Type
from fluke.utils import find_root_proj
from abc import abstractmethod


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
