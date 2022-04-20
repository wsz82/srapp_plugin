import dataclasses
from decimal import Decimal
from .data import Data


@dataclasses.dataclass(frozen=True)
class DrilledWaterHorizon(Data):
    name: str
    horizon: str
    depth: Decimal

    @staticmethod
    def from_dict(point_name, doc_map: {}) -> 'DrilledWaterHorizon':
        return DrilledWaterHorizon(
            point_name,
            doc_map.get('database'),
            doc_map.get('depth'),
        )

    def attrs(self):
        return [
            self.name,
            self.horizon,
            self.depth,
        ]


@dataclasses.dataclass(frozen=True)
class Exudation(Data):
    name: str
    type: str
    depth: Decimal

    @staticmethod
    def from_dict(point_name, doc_map: {}) -> 'Exudation':
        return Exudation(
            point_name,
            doc_map.get('database'),
            doc_map.get('depth'),
        )

    def attrs(self):
        return [
            self.name,
            self.type,
            self.depth,
        ]


@dataclasses.dataclass(frozen=True)
class SetWaterHorizon(Data):
    name: str
    horizon: str
    depth: Decimal
    # measurementPeriod:
    days: int
    hours: int
    minutes: int

    @staticmethod
    def from_dict(point_name, doc_map: {}) -> 'SetWaterHorizon':
        measurement_period = doc_map.get('measurementPeriod')
        return SetWaterHorizon(
            point_name,
            doc_map.get('database'),
            doc_map.get('depth'),
            measurement_period.get('days'),
            measurement_period.get('hours'),
            measurement_period.get('minutes')
        )

    def attrs(self):
        return [
            self.name,
            self.horizon,
            self.depth,
            self.days,
            self.hours,
            self.minutes,
        ]
