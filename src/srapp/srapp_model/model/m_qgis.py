import abc
from typing import *

T = TypeVar('T')


class IQgis(Generic[T]):
    def __init__(self, iface: T):
        self.iface = iface

    @abc.abstractmethod
    def try_refresh(self) -> bool:
        pass
