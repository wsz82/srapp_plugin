import abc
import datetime
from typing import *

from database import data, constants, shear
from database.data import Data, IFeature, FTR
from model import LocalToRemote
from model.m_config import LAYER_NAME_TO_FIELDS_CONSTRAINTS
from model.m_field import FieldConstraint
from model.m_qgis import IQgis
from srapp_model import G

LSTNR = TypeVar('LSTNR')


class IListener(Generic[LSTNR]):
    def __init__(self, obj: LSTNR):
        self.obj = obj

    @abc.abstractmethod
    def stop(self):
        pass


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
        self.name: str = ''

    def _are_fields_invalid(self, features: List[IFeature]) -> bool:
        if not features:
            return False
        messages_container: List[str] = []
        layer_name = self.name
        field_names = self.field_names()
        idx_to_constraints: Dict[int, Set[FieldConstraint]] = LAYER_NAME_TO_FIELDS_CONSTRAINTS.get(layer_name)
        for idx, constraints in idx_to_constraints.items():
            for constraint in constraints:
                if constraint == FieldConstraint.NOT_NULL:
                    for feat in features:
                        attributes = feat.attributes()
                        attr = attributes[idx]
                        if not attr:
                            messages_container.append(
                                f'Pusta wartość pola "{field_names[idx]}" w wierszu numer {feat.fid()}')
                elif constraint == FieldConstraint.UNIQUE:
                    all_features = self.all_features()
                    all_attrs = [f.attributes()[idx] for f in all_features]
                    for feat in features:
                        attributes = feat.attributes()
                        attr = attributes[idx]
                        looked_attrs = list(all_attrs)
                        looked_attrs.remove(attr)
                        if attr in looked_attrs:
                            messages_container.append(
                                f'Nieunikalna wartość pola "{field_names[idx]}" w wierszu numer {feat.fid()}')
                elif constraint == FieldConstraint.SOIL:
                    for feat in features:
                        attributes = feat.attributes()
                        attr = attributes[idx]
                        if attr not in constants.SOIL_TYPES:
                            messages_container.append(
                                f'Nazwa gruntu "{attr}" w polu "{field_names[idx]}" w wierszu numer {feat.fid()} nie mieści się w zakresie {constants.SOIL_TYPES}')
                elif constraint == FieldConstraint.WATER_HORIZON:
                    for feat in features:
                        attributes = feat.attributes()
                        attr = attributes[idx]
                        if attr not in constants.WATER_HORIZONS:
                            messages_container.append(
                                f'Numer warstwy wodonośnej "{attr}" w polu "{field_names[idx]}" w wierszu numer {feat.fid()} nie mieści się w zakresie {constants.WATER_HORIZONS}')
                elif constraint == FieldConstraint.EXUDATION:
                    for feat in features:
                        attributes = feat.attributes()
                        attr = str(attributes[idx])
                        if attr not in constants.EXUDATION_TYPES:
                            messages_container.append(
                                f'Rodzaj sączenia "{attr}" w polu "{field_names[idx]}" w wierszu numer {feat.fid()} nie mieści się w zakresie {constants.EXUDATION_TYPES}')
                elif constraint == FieldConstraint.STATUS:
                    statuses = set(constants.STATUSES_REMOTE_TO_LOCAL.values())
                    for feat in features:
                        attributes = feat.attributes()
                        attr = attributes[idx]
                        if attr and attr not in statuses:
                            messages_container.append(
                                f'Stan wykonania "{attr}" w polu "{field_names[idx]}" w wierszu numer {feat.fid()} nie mieści się w zakresie {statuses}')
                elif constraint == FieldConstraint.SHEARS_NUMBER:
                    depths_set = {f.attribute(shear.SHEAR_DEPTH) for f in features}

                    for depth in depths_set:
                        depth_features = [f for f in features if f.attribute(shear.SHEAR_DEPTH) == depth]
                        shears_torques = [f.attribute(shear.VALUE) for f in depth_features]
                        number_of_torques = len(shears_torques)
                        if number_of_torques != constants.SHEARS_SIZE:
                            messages_container.append(
                                f'Ilość wpisów wartości ścięć "{number_of_torques}" w polu "{field_names[idx]}" w dla głębokośći {depth} powinna wynosić {constants.SHEARS_SIZE}')
        if messages_container:
            tag = 'SRApp - błędy zapisu warstw'
            G.Log.message(f'Nie wysłano zmian do bazy danych. Błędy w warstwie {layer_name}:', tag)
            for message in messages_container:
                G.Log.message(message, tag)
            return True
        return False

    @abc.abstractmethod
    def stop_edit_mode(self):
        pass

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
                fid = feat.fid()
                attr_map = item.attr_map(fid)
                self.change_attribute_values(attr_map)
                self.change_geometry_values(fid, item)
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

    def change_geometry_values(self, feat_id: int, item: Data):
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
            self.fid_to_name.update({f.fid(): f.name() for f in features})
            if self._are_fields_invalid(features):
                return
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
            features = self.features_by_fids(fids)
            if self._are_fields_invalid(features):
                return
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

    @abc.abstractmethod
    def features_by_fids(self, fids: List[int]):
        pass

    @abc.abstractmethod
    def field_names(self):
        pass

    @abc.abstractmethod
    def get_wkid(self) -> int:
        pass


class ListenerLayer(IListener[Callable]):

    @abc.abstractmethod
    def stop(self):
        self.obj()
