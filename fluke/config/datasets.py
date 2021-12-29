from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypedDict, Union
import yaml
from fluke.utils import find_root_proj, run_r
from fluke.logger import init_logger
from fluke.datasets.abstract import AbstractDataset
from fluke.datasets.query_dataset import BigQueryDataset, QueryDataset
from fluke.datasets.csv_dataset import CSVDataset

logger = init_logger()

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




