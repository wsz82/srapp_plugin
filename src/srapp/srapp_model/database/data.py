import abc
import dataclasses
import datetime
from abc import ABC
from typing import *
from typing import Tuple

from google.api_core.datetime_helpers import DatetimeWithNanoseconds

from model import LocalToRemote


def transfer_entry(from_map: dict, to_map: dict, key: str):
    if key in from_map:
        to_map.update({key: from_map.pop(key)})


NAME = 'punkt'
NAME_REMOTE = 'pointNumber'
TIME = 'czas'
TIME_REMOTE = 'timestamp'
# position of field TIME in layers attributes
TIME_POS = 1

PERSON = 'wykonawca'
REMOTE_PERSONS = 'persons'

FTR = TypeVar('FTR')


class IFeature(Generic[FTR]):

    def __init__(self, feature: FTR):
        self.feature = feature

    @abc.abstractmethod
    def fid(self) -> int:
        pass

    def name(self):
        return self.attribute(NAME)

    def time(self):
        return self.attribute(TIME)

    @abc.abstractmethod
    def set_attributes(self, attrs: list):
        pass

    @abc.abstractmethod
    def attribute(self, name: str) -> Any:
        pass

    @abc.abstractmethod
    def attributes(self) -> list:
        pass

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, IFeature):
            return self.fid() == other.fid()
        return NotImplemented

    def __hash__(self):
        """Overrides the default implementation"""
        return hash(self.fid())


class IPointFeature(IFeature, ABC):

    @abc.abstractmethod
    def set_geometry(self, x: float, y: float):
        pass

    @abc.abstractmethod
    def set_spatial_index(self):
        pass

    @abc.abstractmethod
    def xy(self) -> Tuple[float, float]:
        pass


DTTP = TypeVar('DTTP')


@dataclasses.dataclass(frozen=True)
class Data:

    def attr_map(self, feat_id: int) -> Dict[int, dict]:
        attr = self.attrs()
        return {feat_id: {i + 1: val for i, val in enumerate(attr)}}

    def to_feature(self, feature_wrapper: IFeature) -> DTTP:
        feat = feature_wrapper.feature
        attrs: list = self.attrs()
        # feature id
        attrs.insert(0, None)
        feature_wrapper.set_attributes(attrs)
        return feat

    @abc.abstractmethod
    def attrs(self) -> list:
        """Layer database"""
        pass

    def fields_names(self) -> List[str]:
        return self.local_to_remote().local_names()

    @abc.abstractmethod
    def local_to_remote(self) -> LocalToRemote[str, str]:
        pass

    @staticmethod
    def remote_time_to_local(r: DatetimeWithNanoseconds) -> str:
        if not r:
            return ''
        return str(datetime.datetime(r.year, r.month, r.day, r.hour, r.minute, r.second))


@dataclasses.dataclass(frozen=True)
class PointData(Data, ABC):
    x: float
    y: float

    def to_feature(self, feature_wrapper: IPointFeature) -> FTR:
        super().to_feature(feature_wrapper)
        feature_wrapper.set_geometry(self.x, self.y)
        feature_wrapper.set_spatial_index()
        return feature_wrapper.feature
