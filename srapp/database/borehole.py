import dataclasses
from typing import List
from .product import Product
from .product_point import ProductPoint
from .layer import Layer
from .water import DrilledWaterHorizon, SetWaterHorizon, Exudation


@dataclasses.dataclass(frozen=True)
class Borehole(ProductPoint):
    drill_type: str

    def attrs(self):
        return super(Borehole, self).attrs() + [
            self.drill_type
        ]


@dataclasses.dataclass(frozen=True)
class BoreholeProduct(Product):
    borehole: Borehole
    layers: List[Layer]
    drilledWaterHorizons: List[DrilledWaterHorizon]
    setWaterHorizons: List[SetWaterHorizon]
    exudations: List[Exudation]

    @staticmethod
    def from_dict(doc_map: {}) -> 'BoreholeProduct':
        name = doc_map.get('pointNumber')
        last_performer = doc_map.get('lastPerformer')

        point_map = doc_map.get('point')
        persons = point_map.get('persons')
        location = point_map.get('location')
        vehicle_number = point_map.get('vehicleNumber')
        start_depth = point_map.get('startDepth')

        borehole_map = doc_map.get('borehole')
        drill_type = borehole_map.get('drillType')

        borehole = Borehole(persons, location, vehicle_number, start_depth, drill_type)

        layer_doc_list = doc_map.get('layers')
        if layer_doc_list:
            layers = [Layer.from_dict(name, layer_map) for layer_map in layer_doc_list]
        else:
            layers = []

        drilled_water_doc: dict = doc_map.get('drilledWaterHorizons')
        if drilled_water_doc:
            drilled_water = [DrilledWaterHorizon.from_dict(name, water_map) for water_map in drilled_water_doc.values()]
        else:
            drilled_water = []

        set_water_doc: dict = doc_map.get('setWaterHorizons')
        if set_water_doc:
            set_water = [SetWaterHorizon.from_dict(name, water_map) for water_map in set_water_doc.values()]
        else:
            set_water = []

        exudations_doc: dict = doc_map.get('exudations')
        if exudations_doc:
            exudations = [Exudation.from_dict(name, exu_map) for exu_map in exudations_doc.values()]
        else:
            exudations = []

        return BoreholeProduct(name, last_performer, borehole, layers, drilled_water, set_water, exudations)

    def attrs(self):
        return super(BoreholeProduct, self).attrs() + self.borehole.attrs()
