import dataclasses
from typing import *

from database import data
from database.product_point import LAST_PERFORMER_REMOTE, LOCATION_REMOTE, VEHICLE_NUMBER_REMOTE, \
    START_DEPTH_REMOTE
from model import LocalToRemote
from srapp_model.database import product_point
from srapp_model.database.layer import Layer
from srapp_model.database.product import Product
from srapp_model.database.product_point import ProductPoint
from srapp_model.database.water import DrilledWaterHorizon, SetWaterHorizon, Exudation

REMOTE_DRILL_TYPE = 'drillType'
REMOTE_BOREHOLE = 'borehole'

DRILLED_WATER_HORIZONS_REMOTE = 'drilledWaterHorizons'
SET_WATER_HORIZONS_REMOTE = 'setWaterHorizons'
EXUDATIONS_REMOTE = 'exudations'
LAYERS_REMOTE = 'layers'

LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.TIME, data.TIME_REMOTE),
    (data.NAME, data.NAME_REMOTE),
    (product_point.LAST_PERFORMER, LAST_PERFORMER_REMOTE),
    (product_point.LOCATION, LOCATION_REMOTE),
    (product_point.VEHICLE_NUMBER, VEHICLE_NUMBER_REMOTE),
    (product_point.START_DEPTH, START_DEPTH_REMOTE),
    (product_point.TYPE, REMOTE_DRILL_TYPE),
])


def remote_transformation(data_map: Dict[str, str]) -> Dict[str, Any]:
    data_map = product_point.remote_transformation(data_map)
    borehole_map = {}
    data.transfer_entry(data_map, borehole_map, REMOTE_DRILL_TYPE)
    if borehole_map:
        data_map.update({REMOTE_BOREHOLE: borehole_map})
    return data_map


@dataclasses.dataclass(frozen=True)
class Borehole(ProductPoint):
    drill_type: str

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return LOCAL_TO_REMOTE

    def attrs(self) -> list:
        return super().attrs() + [
            self.drill_type
        ]


@dataclasses.dataclass(frozen=True)
class BoreholeProduct(Product):
    borehole: Borehole
    layers: List[Layer]
    drilledWaterHorizons: List[DrilledWaterHorizon]
    setWaterHorizons: List[SetWaterHorizon]
    exudations: List[Exudation]

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return LOCAL_TO_REMOTE

    def attrs(self) -> list:
        return super().attrs() + self.borehole.attrs()

    @staticmethod
    def from_dict(doc_map: dict) -> 'BoreholeProduct':
        timestamp, name, last_performer = Product.product_from_dict(doc_map)
        persons, location, vehicle_number, start_depth = ProductPoint.product_point_from_dict(name, doc_map)

        borehole_map = doc_map.get(REMOTE_BOREHOLE)
        drill_type = borehole_map.get(REMOTE_DRILL_TYPE, '')

        borehole = Borehole(persons, location, vehicle_number, start_depth, drill_type)

        layers_list: list = doc_map.get(LAYERS_REMOTE, [])
        layers = [Layer.from_dict(name, layer_map) for layer_map in layers_list]

        drilled_water_list: list = doc_map.get(DRILLED_WATER_HORIZONS_REMOTE, [])
        drilled_water = [DrilledWaterHorizon.from_dict(name, water_doc) for water_doc in drilled_water_list]

        set_water_list: list = doc_map.get(SET_WATER_HORIZONS_REMOTE, [])
        set_water = [SetWaterHorizon.from_dict(name, water_map) for water_map in set_water_list]

        exudations_list: list = doc_map.get(EXUDATIONS_REMOTE, [])
        exudations = [Exudation.from_dict(name, exu_map) for exu_map in exudations_list]

        return BoreholeProduct(timestamp, name, last_performer, borehole, layers, drilled_water, set_water, exudations)
