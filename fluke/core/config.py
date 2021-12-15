from __future__ import annotations
import json
import collections
from pathlib import Path
from abc import ABC, abstractmethod
from typing import (
    Iterable,
    List,
    TypedDict,
    Optional,
    TYPE_CHECKING
)
import click
from typing import OrderedDict
from fluke.core.objects.table import TableVersion
from fluke.core.utils import find_root_proj

if TYPE_CHECKING:
    from fluke.core.objects import Table
    from fluke.core.objects import Dataset
    from fluke.core.database import DatabaseInfo

class TableInfo(TypedDict):
    name: Optional[str]
    src: Optional[str]
    versions: List[str]


class TableVersionInfo(TypedDict):
    name: Optional[str]
    version: Optional[str]


class DatasetInfo(TypedDict):
    name: Optional[str]
    table_versions: List[TableVersionInfo]


class Config(ABC):
    """Abstract Class for Config classes"""
    @abstractmethod
    def _check_params(self):
        """From """
        ...

    @abstractmethod
    def r_argument(self) -> List[str]:
        """Construct R arguments from class attributes"""
        ...

    @abstractmethod
    def to_write(self):
        ...


class Tables(Config):
    """
    A Python Class representation of tables as configured in
    sherpa-config.json
    """
    def __init__(self, info: Iterable[TableInfo]):
        from fluke.core.objects import Table
        tables: OrderedDict[str, Table] = collections.OrderedDict()

        for table_info in info:
            versions: OrderedDict[str, TableVersion] = collections.OrderedDict()
            if table_info['name'] is not None and table_info['src'] is not None:
                for version in table_info['versions']:
                    versions[version] = TableVersion(table_info['name'], version)
                src_full_path = Path(find_root_proj(), 'src/data_pull/', table_info['src'])
                tables[table_info['name']] = Table(src_full_path, versions)

        self.tables = tables

    def __call__(self):
        return self.tables

    def add(self, table: Table) -> None:
        """Add a new table."""
        self.tables[table.name] = table

    def get(self, tbl_name: str) ->  Table:
        try:
            return self.tables[tbl_name]
        except click.UsageError as no_table_name:
            raise click.UsageError(
                ("The table name `%s` is not yet implemented under src/data_pull. "
                "Create script `create_%s.R`."
                ) % (tbl_name, tbl_name)
            ) from no_table_name

    def to_write(self) -> Iterable[TableInfo]:
        """Convert back config to info, ready for dumping as json."""
        if len(self.tables) == 0:
            return  [
                TableInfo(
                name=None,
                src=None,
                versions=[])
            ]

        info_list = []
        for name, _table in self.tables.items():
            versions = []
            for ver, _ in _table.versions.items():
                versions.append(ver)
            if _table.src is not None:
                src = str(_table.src.stem)

            info_list.append(
                TableInfo(
                    name=name,
                    src=src,
                    versions=versions)
            )
        return info_list



    def _check_params(self) -> None:
        raise NotImplementedError

    def r_argument(self) -> List[str]:
        raise NotImplementedError


class Datasets(Config):
    """A Python Class representation of datasets as configured in sherpa-config.json"""
    def __init__(self, info: Iterable[DatasetInfo]):
        from fluke.core.objects import Dataset
        datasets: OrderedDict[str, Dataset] = collections.OrderedDict()

        for ds_info in info:
            table_versions: OrderedDict[str, TableVersion] = collections.OrderedDict()
            for tbl_version_info in ds_info['table_versions']:
                if tbl_version_info['name'] is not None and tbl_version_info['version'] is not None:
                    table_versions[tbl_version_info['name']] = TableVersion(
                        tbl_version_info['name'],
                        tbl_version_info['version'])
            if ds_info['name'] is not None:
                datasets[ds_info['name']] = Dataset(ds_info['name'], table_versions)

        self.datasets = datasets

    def __call__(self):
        return self.datasets

    def add(self, dataset: Dataset):
        """Add a new dataset."""
        self.datasets[dataset.name] = dataset

    def get(self, ds_name: str):
        try:
            return self.datasets[ds_name]
        except click.UsageError as no_ds_name:
            raise click.UsageError(
                "The dataset `%s` has not been created yet "
            ) from no_ds_name

    def to_write(self) -> Iterable[DatasetInfo]:
        """Revert config to DatasetInfo, ready for writing."""
        if len(self.datasets) == 0:
            return [
                DatasetInfo(
                    name=None,
                    table_versions=[
                        TableVersionInfo(name=None, version=None)
                    ]
                )
            ]

        info_list = []
        for name, _dataset in self.datasets.items():
            table_versions = []
            for tbl_name, tbl_ver in _dataset.table_versions.items():
                table_versions.append(
                    TableVersionInfo(name=tbl_name, version=tbl_ver.version)
                )
            info_list.append(
                DatasetInfo(name=name, table_versions=table_versions)
            )


        return info_list


    def _check_params(self):
        ...

    def r_argument(self) -> List[str]:
        ...


class ProjectInfo(TypedDict):
    """Definition of a project config statically typed."""
    sherpa_version: str
    r_version: str
    targets_version: str
    database: DatabaseInfo
    tables: List[TableInfo]
    datasets: List[DatasetInfo]


def read_project_config(proj_root: Path) -> ProjectInfo:
    """from proj_root, get config from project-config.yml"""
    cfg = Path(proj_root, 'sherpa-config.json')
    return json.load(cfg.open('r', encoding='utf-8'))


class Project:
    """A python class representation of sherpa-config.json"""
    def __init__(self):
        from fluke.core.database import get_database_cls
        self.proj_root_path = find_root_proj()
        self.proj_config_dict = read_project_config(self.proj_root_path)

        # instantiating specific configs mapped to parts in project level config
        self.database = get_database_cls(self.proj_config_dict['database'])
        self.tables =  Tables(self.proj_config_dict['tables'])
        self.datasets = Datasets(self.proj_config_dict['datasets'])

    def write(self):
        self.proj_config_dict['tables'] = self.tables.to_write()
        self.proj_config_dict['datasets'] = self.datasets.to_write()
        path_to_config = Path(self.proj_root_path, 'sherpa-config.json')

        json.dump(self.proj_config_dict, path_to_config.open('w', encoding='utf-8'),
        indent=2)




