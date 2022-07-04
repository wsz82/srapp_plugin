import dataclasses
from typing import *

from database import data, product_point, shear
from database.product_point import LAST_PERFORMER_REMOTE, LOCATION_REMOTE, VEHICLE_NUMBER_REMOTE, \
    START_DEPTH_REMOTE
from model import LocalToRemote
from srapp_model.database.data import Data
from srapp_model.database.product import Product
from srapp_model.database.product_point import ProductPoint
from srapp_model.database.shear import ShearUnit

REMOTE_PROBE = 'probe'
REMOTE_SHEARS = 'shears'

PROBE_TYPE_REMOTE = 'probeType'
INTERVAL_REMOTE = 'interval'
UNITS_REMOTE = 'units'

VALUE = 'wartosc'
INDEX = 'indeks'

PROBE_TYPE = 'typ'
INTERVAL = 'interwal'
LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.TIME, data.TIME_REMOTE),
    (data.NAME, data.NAME_REMOTE),
    (product_point.LAST_PERFORMER, LAST_PERFORMER_REMOTE),
    (product_point.LOCATION, LOCATION_REMOTE),
    (product_point.VEHICLE_NUMBER, VEHICLE_NUMBER_REMOTE),
    (product_point.START_DEPTH, START_DEPTH_REMOTE),
    (PROBE_TYPE, PROBE_TYPE_REMOTE),
    (INTERVAL, INTERVAL_REMOTE),
])


def remote_transformation(data_map: Dict[str, str]) -> Dict[str, Any]:
    data_map = product_point.remote_transformation(data_map, REMOTE_PROBE)
    probe_map = {}
    data.transfer_entry(data_map, probe_map, PROBE_TYPE_REMOTE)
    data.transfer_entry(data_map, probe_map, INTERVAL_REMOTE)
    data.transfer_entry(data_map, probe_map, UNITS_REMOTE)
    if probe_map:
        data_map.update({REMOTE_PROBE: probe_map})
    return data_map


def probe_unit_local_names() -> List[str]:
    return [
        data.NAME,
        INDEX,
        VALUE
    ]


@dataclasses.dataclass(frozen=True)
class ProbeUnit(Data):
    name: str
    index: int
    value: str

    def attrs(self) -> list:
        return [
            self.name,
            self.index,
            self.value,
        ]


@dataclasses.dataclass(frozen=True)
class Probe(ProductPoint):
    probeType: str
    interval: float
    units: List[ProbeUnit]

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return LOCAL_TO_REMOTE

    def attrs(self) -> list:
        return super().attrs() + [
            self.probeType,
            self.interval,
        ]


@dataclasses.dataclass(frozen=True)
class ProbeProduct(Product, Data):
    probe: Probe
    shears: List[ShearUnit]

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return LOCAL_TO_REMOTE

    def attrs(self) -> list:
        return super().attrs() + self.probe.attrs()

    @staticmethod
    def from_dict(doc_map: dict) -> 'ProbeProduct':
        timestamp, name, last_performer = Product.product_from_dict(doc_map)
        persons, location, vehicle_number, start_depth = ProductPoint.product_point_from_dict(name, doc_map,
                                                                                              REMOTE_PROBE)

        probe_map = doc_map.get(REMOTE_PROBE)
        probe_type = probe_map.get(PROBE_TYPE_REMOTE, '')
        interval = float(probe_map.get(INTERVAL_REMOTE, 0))
        raw_values_list: List[str] = probe_map.get(UNITS_REMOTE, [])
        units_list = [ProbeUnit(name, idx, value) for idx, value in enumerate(raw_values_list)]

        probe = Probe(persons, location, vehicle_number, start_depth, probe_type, interval, units_list)
        raw_shears_list: List[dict] = doc_map.get(REMOTE_SHEARS, [])
        all_shear_units = []
        for shear_map in raw_shears_list:
            depth = float(shear_map.get(shear.SHEAR_DEPTH_REMOTE, ''))
            shear_units = [ShearUnit(name, depth, idx, torque) for idx, torque in
                           enumerate(shear_map.get(shear.TORQUES_REMOTE))]
            all_shear_units += shear_units
        return ProbeProduct(timestamp, name, last_performer, probe, all_shear_units)
