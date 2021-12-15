import collections
from dataclasses import dataclass, field
import collections
from pathlib import Path
from typing import OrderedDict, Dict, Optional
from fluke.core.objects.table import TableVersion
from fluke.core.utils import find_root_proj

@dataclass
class Dataset:
    name: str
    table_versions: OrderedDict[str, TableVersion] = field(default_factory=collections.OrderedDict)

    def __post_init__(self):
        self.path_to_dataset = Path(find_root_proj(), 'datasets', self.name)

    def create_dataset_dir(self):
        """Creates the directory to encapsulate relevant dataset files."""
        self.path_to_dataset.mkdir(parents = True, exist_ok=True)

    def add(self, table_version: TableVersion):
        """Add a TableVersion object."""
        self.table_versions[table_version.name] = table_version

