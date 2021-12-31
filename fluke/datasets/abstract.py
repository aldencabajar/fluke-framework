"""Abstract methods for Dataset-related Classes"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypedDict, Union


class AbstractParam(ABC):
    """Abstract class for Param-like Classes."""
    @abstractmethod
    def _check_params(self) -> None:
        ...


class AbstractDataset(ABC):
    """Abstract class for Dataset Classes"""
    @abstractmethod
    def __init__(self, name: str, params: Dict[str, Optional[Any]]) -> None:
        self.name = name
        self._set_params(params)

    @abstractmethod
    def tar_cmd(self) -> str:
        """abstract method to construct command for `targets`."""
        ...

    @abstractmethod
    def _set_params(self, params: Dict[str, Any]) -> None:
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

