import collections
import re
from pathlib import Path
from typing import List, Optional, OrderedDict, Union
from fluke.core.objects import SherpaObject
from fluke.core.utils import Cadence, find_root_proj
from dataclasses import dataclass, field


@dataclass
class TableVersion:
    name: str
    version: str

    def cat_table_version(self) -> str:
        """concatenate table and version."""
        tbl_version_cat = '_'.join([self.name, self.version])
        return tbl_version_cat

    def get_path(self) -> Path:
        """From name, get the path to source."""
        src_file = f'create_{self.name}.R'
        return Path(find_root_proj(), 'src/data_pull', src_file)


@dataclass
class Table:
    """"Class to encapsulate attributes about tables to be created."""
    src: Optional[Path]
    versions: OrderedDict[str, TableVersion] = field(default_factory=collections.OrderedDict)

    def __post_init__(self) -> None:
        ptr = re.compile(r'^create_(.*)')

        if self.src is not None:
            search = ptr.search(self.src.stem)
            self.name = search.group(1)
        else:
            self.name = None

    def add(self, kw: str):
        """Adds a new version to the list of TableVersions"""
        ver = self._derive_version(kw)
        self.versions[ver] = TableVersion(self.name, ver)

    def _derive_version(self, kw: str):
        if kw in Cadence.cadence_options:
            ver = Cadence(kw).version()
        else:
            ver = kw
        return ver

    def get(self, ver: str):
        """obtain the corresponding table version from `ver` str."""
        return self.versions[ver]

    def most_recent_ver(self):
        """get the most recent version"""
        return next(reversed(self.versions.values()))



