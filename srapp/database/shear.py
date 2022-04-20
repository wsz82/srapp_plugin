from qgis._core import QgsFeature

from .data import Data
from decimal import Decimal
from typing import List
import dataclasses


@dataclasses.dataclass(frozen=True)
class Shear(Data):
    name: str
    depth: Decimal
    torques: List[str]

    def attrs(self) -> []:
        return [
            self.name,
            self.depth,
            ','.join(self.torques)
        ]

    @staticmethod
    def from_dict(name, doc_map) -> 'Shear':
        return Shear(
            name,
            doc_map.get('depth'),
            doc_map.get('torques')
        )


POINT = 'punkt'
SHEAR_DEPTH = 'gl_sciec'


@dataclasses.dataclass(frozen=True)
class TodoShear(Data):
    name: str
    depth: Decimal

    def attrs(self) -> []:
        return [
            self.name,
            self.depth
        ]

    @staticmethod
    def from_feature(feat: QgsFeature):
        return TodoShear(
            TodoShear.get_attribute_value(feat, POINT),
            TodoShear.get_attribute_value(feat, SHEAR_DEPTH)
        )
