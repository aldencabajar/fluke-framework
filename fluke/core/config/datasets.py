from pathlib import Path
from copy import copy
from typing import Any, Dict, List, Mapping, Optional, Type, TypedDict
import yaml
from dataclasses import dataclass, field
from abc import (
    ABC,
    ABCMeta,
    abstractmethod,
    abstractclassmethod,
    abstractproperty
)
from fluke.core.utils import find_root_proj, run_r


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

    def __init__(self, name: str, params: Dict[str, Optional[Any]]) -> None:
        super().__init__(name, params)

    def _set_params(self, params: Dict[str, Optional[Any]]) -> None:
        _params = self._param_struct(**params)
        self.params = _params

    def tar_cmd(self) -> str:
        if self.params.read_fun_args is not None:
            arg_exprs = []
            for k, v in self.params.read_fun_args.items():
                arg_exprs.append(
                    f'{k} = {v}'
                )
            arg_expr_all = ','.join(arg_exprs)
            read_cmd = f'{self.params.read_fun}("{str(self.params.location)}", {arg_expr_all})'
        else:
            read_cmd = f'{self.params.read_fun}("{str(self.params.location)}")'

        cmd = f'tar_target({self.name}, {read_cmd})'

        return cmd


def dataset_class_factory(
    dataset_type: str,
    name: str,
    params: Dict[str, Optional[Any]]
    ) -> AbstractDataset:
    """
    generates an instantiated Dataset Class from name and params.
    """

    datasets: Dict[str, Type[AbstractDataset]] = {
        'csv' : CSVDataset
    }

    dataset_object = datasets[dataset_type](name, params)

    return dataset_object



class DatasetConfig(TypedDict):
    type: str
    params: Dict[str, Optional[Any]]

class Datasets:
    """Class to be instantiated to encapsulate datasets info."""
    def __init__(self, version):
        self.version = version
        self.ds_config_path = Path(find_root_proj(), 'config', 'datasets.yaml')
        with self.ds_config_path.open('r', encoding='utf-8') as cfg:
            try:
                ds_config: Dict[str, DatasetConfig] = yaml.safe_load(cfg)['datasets']
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

    def __next__(self):
        out = self._list[self._index]
        self._index += 1

        return out

    def __len__(self):
        return len(self._list)

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
            store = 'datasets/stores/{self.version}',
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




