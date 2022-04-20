import dataclasses
from .data import Data


@dataclasses.dataclass(frozen=True)
class Product(Data):
    name: str
    last_performer: str

    def attrs(self) -> []:
        return [
            self.name,
            self.last_performer
        ]
