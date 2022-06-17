from typing import *


class LocalToRemote(OrderedDict):

    def __setitem__(self, key, value):
        if value in self.values():
            raise ValueError(f'{self} already contains "{value}"')
        super(LocalToRemote, self).__setitem__(key, value)

    def key(self, value):
        values = self.values()
        if value not in values:
            return None
        idx = list(values).index(value)
        return list(self.keys())[idx]

    def local_names(self) -> list:
        return list(self.keys())

    def remote_names(self) -> list:
        return list(self.values())
