import dataclasses
from typing import List
from .product import Product
from .product_point import ProductPoint
from .data import Data
from .shear import Shear
from decimal import Decimal


@dataclasses.dataclass(frozen=True)
class Probe(ProductPoint):
    probeType: str
    interval: Decimal
    units: List[str]

    def attrs(self) -> []:
        """Layer database with fid"""
        return super(Probe, self).attrs() + [
            self.probeType,
            self.interval,
            ','.join(self.units)
        ]


@dataclasses.dataclass(frozen=True)
class ProbeProduct(Product, Data):
    probe: Probe
    shears: List[Shear]

    def attrs(self) -> []:
        return super(ProbeProduct, self).attrs() + self.probe.attrs()

    @staticmethod
    def from_dict(doc_map: {}) -> 'ProbeProduct':
        name = doc_map.get('pointNumber')
        last_performer = doc_map.get('lastPerformer')

        point_map = doc_map.get('point')
        persons = point_map.get('persons')
        location = point_map.get('location')
        vehicle_number = point_map.get('vehicleNumber')
        start_depth = point_map.get('startDepth')

        probe_map = doc_map.get('probe')
        probe_type = probe_map.get('probeType')
        interval = probe_map.get('interval')
        units_list = probe_map.get('units')

        probe = Probe(persons, location, vehicle_number, start_depth, probe_type, interval, units_list)
        shears_doc_list = doc_map.get('shears')
        shears = [Shear.from_dict(name, shear_map) for shear_map in shears_doc_list]
        return ProbeProduct(name, last_performer, probe, shears)

    def attrs(self):
        """Layer database with fid"""
        return super(ProbeProduct, self).attrs() + self.probe.attrs()
