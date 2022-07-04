import dataclasses

from database import data
from model import LocalToRemote
from srapp_model.database.data import Data

REMOTE_DATA = 'data'
WATER_DEPTH_REMOTE = 'depth'
WATER_DEPTH = 'gl_zwier'

HORIZON = 'warstwa'
TIME_REMOTE = 'time'
TIME_PERIOD_MIN = 'okres_min'

DRILLED_WATER_LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.NAME, data.NAME_REMOTE),
    (HORIZON, REMOTE_DATA),
    (WATER_DEPTH, WATER_DEPTH_REMOTE),
    (data.TIME, TIME_REMOTE),
])


@dataclasses.dataclass(frozen=True)
class DrilledWaterHorizon(Data):
    name: str
    horizon: str
    depth: float
    time: str

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return DRILLED_WATER_LOCAL_TO_REMOTE

    @staticmethod
    def from_dict(point_name, doc_map: dict) -> 'DrilledWaterHorizon':
        return DrilledWaterHorizon(
            point_name,
            doc_map.get(REMOTE_DATA),
            float(doc_map.get(WATER_DEPTH_REMOTE)),
            Data.remote_time_to_local(doc_map.get(TIME_REMOTE)),
        )

    def attrs(self):
        return [
            self.name,
            self.horizon,
            self.depth,
            self.time,
        ]


SET_WATER_LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.NAME, data.NAME_REMOTE),
    (HORIZON, REMOTE_DATA),
    (WATER_DEPTH, WATER_DEPTH_REMOTE),
    (data.TIME, TIME_REMOTE),
    (TIME_PERIOD_MIN, None),
])


@dataclasses.dataclass(frozen=True)
class SetWaterHorizon(Data):
    name: str
    horizon: str
    depth: float
    time: str
    measurement_period_min: int

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return SET_WATER_LOCAL_TO_REMOTE

    @staticmethod
    def from_dict(point_name, doc_map: {}) -> 'SetWaterHorizon':
        all_minutes = 0
        measurement_period: dict = doc_map.get('measurementPeriod')
        if measurement_period:
            days = measurement_period.get('days', 0)
            hours = measurement_period.get('hours', 0)
            minutes = measurement_period.get('minutes', 0)
            all_minutes = days * 24 * 60 + hours * 60 + minutes
        return SetWaterHorizon(
            point_name,
            doc_map.get(REMOTE_DATA),
            float(doc_map.get(WATER_DEPTH_REMOTE)),
            Data.remote_time_to_local(doc_map.get(TIME_REMOTE)),
            all_minutes,
        )

    def attrs(self):
        return [
            self.name,
            self.horizon,
            self.depth,
            self.time,
            self.measurement_period_min,
        ]


EXUDATION_TYPE = 'rodz_sacz'
EXUDATION_DEPTH = 'glebok'
EXUDATION_LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.NAME, data.NAME_REMOTE),
    (EXUDATION_TYPE, REMOTE_DATA),
    (EXUDATION_DEPTH, WATER_DEPTH_REMOTE),
    (data.TIME, TIME_REMOTE),
])


@dataclasses.dataclass(frozen=True)
class Exudation(Data):
    name: str
    type: str
    depth: float
    time: str

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return EXUDATION_LOCAL_TO_REMOTE

    @staticmethod
    def from_dict(point_name, doc_map: {}) -> 'Exudation':
        return Exudation(
            point_name,
            doc_map.get(REMOTE_DATA),
            float(doc_map.get(WATER_DEPTH_REMOTE)),
            Data.remote_time_to_local(doc_map.get(TIME_REMOTE)),
        )

    def attrs(self):
        return [
            self.name,
            self.type,
            self.depth,
            self.time,
        ]
