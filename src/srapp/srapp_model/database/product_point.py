import dataclasses
from abc import ABC
from typing import *

from database.data import REMOTE_PERSONS
from database.person import Person
from srapp_model.database import data
from srapp_model.database.data import Data

REMOTE_POINT = 'point'

LAST_PERFORMER = 'ost_wykon'
LOCATION = 'lokacja'
VEHICLE_NUMBER = 'nr_poj'
START_DEPTH = 'gl_pocz'
TYPE = 'typ'

LAST_PERFORMER_REMOTE = 'lastPerformer'
LOCATION_REMOTE = 'location'
VEHICLE_NUMBER_REMOTE = 'vehicleNumber'
START_DEPTH_REMOTE = 'startDepth'


def remote_transformation(data_map: Dict[str, str], map_key: str) -> Dict[str, Any]:
    point_map = {}
    data.transfer_entry(data_map, point_map, LOCATION_REMOTE)
    data.transfer_entry(data_map, point_map, VEHICLE_NUMBER_REMOTE)
    data.transfer_entry(data_map, point_map, START_DEPTH_REMOTE)
    if point_map:
        data_map.update({map_key: point_map})
    return data_map


@dataclasses.dataclass(frozen=True)
class ProductPoint(Data, ABC):
    persons: List[Person]
    location: str
    vehicle_number: str
    start_depth: float

    def attrs(self) -> list:
        return [
            self.location,
            self.vehicle_number,
            self.start_depth
        ]

    @staticmethod
    def product_point_from_dict(name: str, doc_map: dict, map_key: str) -> Tuple[List[Person], str, str, float]:
        point_map = doc_map.get(map_key)
        persons = []
        raw_persons = point_map.get(REMOTE_PERSONS, [])
        if type(raw_persons) == str:
            persons.append(raw_persons)
        else:
            persons = raw_persons
        persons = [Person(name, person) for person in persons]
        location = point_map.get(LOCATION_REMOTE, '')
        vehicle_number = point_map.get(VEHICLE_NUMBER_REMOTE, '')
        start_depth = float(point_map.get(START_DEPTH_REMOTE) or 0)
        return persons, location, vehicle_number, start_depth
