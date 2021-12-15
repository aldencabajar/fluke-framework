import re
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass

class SherpaObject(ABC):
    @abstractmethod
    def set_version(self, kw: str):
        try:
            cad = Cadence(kw)
            self.version = cad.version()
        except Exception:
            self.version = kw

class Cadence:
    cadence_options = ['day', 'week', 'month']

    def __init__(self, kw: str):
        self.kw = kw
        if not self.is_opt_implemented():
            raise NotImplementedError(
                ('cadence `%s` not yet implemented. Please choose among %s.')
                % (self.kw, ', '.join(self.cadence_options))
            )

    def is_opt_implemented(self) -> bool:
        return self.kw in self.cadence_options

    def version(self):
        datenow = datetime.now()
        if self.kw == 'day':
            return datenow.strftime('%Y%m%d')
        elif self.kw == 'month':
            return datenow.strftime('%Y%m')
        elif self.kw == 'week':
            return datenow.strftime('%Y%md%d')
