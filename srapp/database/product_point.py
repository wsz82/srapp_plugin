import dataclasses
from decimal import Decimal
from typing import List
from .data import Data


@dataclasses.dataclass(frozen=True)
class ProductPoint(Data):
    persons: List[str]
    location: str
    vehicle_number: str
    start_depth: Decimal

    def attrs(self) -> []:
        return [
            ', '.join(self.persons),
            self.location,
            self.vehicle_number,
            self.start_depth
        ]
