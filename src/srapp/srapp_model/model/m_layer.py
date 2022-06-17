import abc
import datetime
import enum
from typing import *

from database import data
from database.data import Data, IFeature, FTR
from model import LocalToRemote
from model.m_qgis import IQgis

LSTNR = TypeVar('LSTNR')


class IListener(Generic[LSTNR]):
    def __init__(self, obj: LSTNR):
        self.obj = obj

    @abc.abstractmethod
    def stop(self):
        pass


class LayerType(enum.Enum):
    ITEM = 0
    SUBITEM_LIST = 1
    SUBITEM_MAP = 2


LR = TypeVar('LR')


class IMapLayer(Generic[LR]):

    def __init__(self, layer: LR, qgis: IQgis):
        self.layer = layer
        self.qgis = qgis
        self.fid_to_name: Dict[int, str] = dict()
        self.database_ref_path: str = None
        self.local_to_remote: LocalToRemote = None
        self.remote_transformation: Callable[Dict[str, str], Dict[str, Any]] = None
        self.features_to_remote: Callable[List[IFeature], dict] = None
        self.can_make_timestamp_on_added = False
        self.project: 'Project' = None

    @abc.abstractmethod
    def id(self):
        pass

    @abc.abstractmethod
    def refresh(self):
        pass

    def add_features(self, items: List[Data], name: str):
        features = self.features_by_name(name)
        rows = max(len(items), len(features))
        feat_and_item = (
            [
                features[i] if len(features) > i else None,
                items[i] if len(items) > i else None
            ]
            for i in range(rows)
        )
        for feat, item in feat_and_item:
            if feat and item:
                attr_map = item.attr_map(feat.fid())
                self.change_attribute_values(attr_map)
            elif feat:
                self._delete_features(feat.fid())
            elif item:
                self._add_feature(item)
                self.update_fid_to_name(name)

    def update_fid_to_name(self, name):
        features = self.features_by_name(name)
        for feature in features:
            self.fid_to_name.update({feature.fid(): name})

    @abc.abstractmethod
    def _add_feature(self, item: Data):
        pass

    @abc.abstractmethod
    def _delete_features(self, id: int):
        pass

    def add_feature(self, item: Data, name: str):
        self.add_features([item], name)

    def feature_by_name(self, name: str) -> IFeature:
        features: [] = self.features_by_name(name)
        assert len(features) < 2
        return features[0] if features else None

    @abc.abstractmethod
    def features_by_name(self, name: str) -> List[IFeature]:
        pass

    @abc.abstractmethod
    def all_features(self) -> List[IFeature]:
        pass

    @abc.abstractmethod
    def change_attribute_values(self, attr_map: Dict[int, Dict[int, Any]]):
        pass

    @abc.abstractmethod
    def delete_all_features(self):
        pass

    @abc.abstractmethod
    def delete_features_by_name(self, name: str):
        pass

    def committed_features_added(self, func_to_call: Callable[['IMapLayer', List[IFeature]], None]) -> IListener:
        def wrapping_func(layer_id: str, raw_features: Iterable[FTR]):
            features = [self.wrap_raw_feature(feat) for feat in raw_features]
            if self.can_make_timestamp_on_added:
                for feat in features:
                    self.make_timestamp(feat.fid())
            func_to_call(self, features)
            self.refresh()

        return IMapLayer.attach_listener(self._committed_features_added_func(), wrapping_func)

    @abc.abstractmethod
    def _committed_features_added_func(self) -> callable:
        pass

    def committed_features_removed(self, func_to_call: callable) -> IListener:
        def wrapping_func(layer_id: str, removed_features_fids: List[int]):
            func_to_call(self, removed_features_fids)
            self.refresh()

        return IMapLayer.attach_listener(self._committed_features_removed_func(), wrapping_func)

    @abc.abstractmethod
    def _committed_features_removed_func(self) -> callable:
        pass

    def committed_attribute_values_changes(self,
                                           func_to_call: Callable[['IMapLayer', List[IFeature]], None]) -> IListener:
        def wrapping_func(layer_id: str, changed_attrs_values: Dict[int, Dict[int, Any]]):
            fids = list(changed_attrs_values.keys())
            features = []
            for fid in fids:
                features += self.features_by_name(self.fid_to_name.get(fid))
            if self.can_make_timestamp_on_added:
                for feat in features:
                    self.make_timestamp(feat.fid())
            func_to_call(self, features)

        return IMapLayer.attach_listener(self._committed_attribute_values_changes_func(), wrapping_func)

    @abc.abstractmethod
    def _committed_attribute_values_changes_func(self) -> callable:
        pass

    @abc.abstractmethod
    def wrap_raw_feature(self, feature: FTR) -> IFeature:
        pass

    @staticmethod
    def attach_listener(to: callable, action: callable):
        to.connect(action)
        return ListenerLayer(lambda: to.disconnect(action))

    def make_timestamp(self, feat_id: int):
        timestamp = datetime.datetime.now()
        self.change_attribute_values({feat_id: {data.TIME_POS: self.make_timestamp_field(timestamp)}})

    @abc.abstractmethod
    def make_timestamp_field(self, timestamp: datetime.datetime):
        pass

    @abc.abstractmethod
    def set_editable(self, editable: bool):
        pass

    def set_project(self, project):
        self.project = project


class ListenerLayer(IListener[Callable]):

    @abc.abstractmethod
    def stop(self):
        self.obj()
