"""CSV Dataset Class."""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict,Optional, Type
from fluke.datasets.abstract import AbstractParam, AbstractDataset
from fluke.utils import (
    dict_to_r_args,
    find_root_proj,
    tar_cmd_generator,
    dict_insert
)

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

    def _set_params(self, params: Dict[str, Any]) -> None:
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

