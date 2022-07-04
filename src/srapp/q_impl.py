import datetime
from typing import *

from PyQt5.QtCore import QVariant, QDateTime
from PyQt5.QtWidgets import QMessageBox
from qgis._core import QgsFeature, QgsGeometry, QgsPointXY, QgsSpatialIndex, QgsMessageLog, QgsVectorLayer, \
    QgsExpression, QgsFeatureRequest

import logger
from database.data import IPointFeature
from model.m_layer import IMapLayer
from srapp_model.database import data
from srapp_model.database.data import FTR
from srapp_model.database.data import IFeature
from srapp_model.logger import ILogger
from srapp_model.model.m_qgis import IQgis


class Feature(IFeature[QgsFeature]):

    def fid(self) -> int:
        return self.feature.id()

    def set_attributes(self, attrs: list):
        self.feature.setAttributes(attrs)

    def attribute(self, name: str) -> Any:
        attribute = self.feature.attribute(name)
        return Feature.filter_attr(attribute)

    def attributes(self) -> list:
        result = []
        attrs: list = self.feature.attributes()
        for attr in attrs:
            result.append(Feature.filter_attr(attr))
        return result

    @staticmethod
    def filter_attr(attr):
        if isinstance(attr, QDateTime):
            attr: QDateTime
            return attr.toPyDateTime()
        return attr if not isinstance(attr, QVariant) else None


class PointFeature(Feature, IPointFeature):

    def xy(self) -> Tuple[float, float]:
        feature: QgsFeature = self.feature
        geometry = feature.geometry()
        if not geometry:
            return 0, 0
        p = geometry.asPoint()
        x = p.x()
        y = p.y()
        return x, y

    def set_geometry(self, x: float, y: float):
        self.feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))

    def set_spatial_index(self):
        index = QgsSpatialIndex()
        index.addFeature(self.feature)


class Logger(ILogger):
    def message(self, message: str, tag: str = logger.DEFAULT_MESSAGE_TAG):
        QgsMessageLog.logMessage(message, tag)

    def error(self, message: str, tag: str = logger.DEFAULT_ERROR_TAG):
        QgsMessageLog.logMessage(message, tag)

    def information(self, message: str, title: str = logger.DEFAULT_INFO_TITLE):
        QMessageBox.information(None, title, message)


class Qgis(IQgis):

    def try_refresh(self) -> bool:
        can_refresh = not self.iface.mapCanvas().isCachingEnabled()
        if can_refresh:
            self.iface.mapCanvas().refresh()
        return can_refresh


class MapLayer(IMapLayer[QgsVectorLayer]):

    def field_names(self):
        return self.layer.fields().names()

    def features_by_fids(self, fids: List[int]):
        all_features = self.all_features()
        return [f for f in all_features if f.fid() in fids]

    def stop_edit_mode(self):
        self.layer.commitChanges(True)

    def make_timestamp_field(self, timestamp: datetime.datetime):
        return QDateTime(timestamp)

    def all_features(self) -> List[IFeature]:
        return [Feature(feat) for feat in self.layer.dataProvider().getFeatures()]

    def _add_feature(self, item):
        feature = item.to_feature(self.wrap_raw_feature(QgsFeature()))
        self.layer.dataProvider().addFeature(feature)

    def _delete_features(self, fid: int):
        self.layer.dataProvider().deleteFeatures([fid])

    def delete_features_by_name(self, name: str):
        layer_features = self.features_by_name(name)
        if layer_features:
            provider = self.layer.dataProvider()
            provider.deleteFeatures([feat.fid() for feat in layer_features])

    def features_by_name(self, name: str) -> List[IFeature]:
        expression = QgsExpression(f'"{data.NAME}"=\'{name}\'')
        raw_features = self.layer.dataProvider().getFeatures(QgsFeatureRequest(expression))
        features = [self.wrap_raw_feature(f) for f in raw_features]
        return list(features) if features else []

    def refresh(self):
        if not self.qgis.try_refresh():
            self.layer.triggerRepaint()

    def change_attribute_values(self, attr_map: Dict[int, Dict[int, Any]]):
        self.layer.dataProvider().changeAttributeValues(attr_map)

    def id(self):
        return self.layer.id()

    def wrap_raw_feature(self, feature: FTR):
        return Feature(feature)

    def _committed_features_added_func(self) -> callable:
        return self.layer.committedFeaturesAdded

    def _committed_features_removed_func(self) -> callable:
        return self.layer.committedFeaturesRemoved

    def _committed_attribute_values_changes_func(self) -> callable:
        return self.layer.committedAttributeValuesChanges

    def delete_all_features(self):
        provider = self.layer.dataProvider()
        list_of_ids = [feat.id() for feat in provider.getFeatures()]
        provider.deleteFeatures(list_of_ids)

    def set_editable(self, editable: bool):
        self.layer.setReadOnly(not editable)


class PointsMapLayer(MapLayer):

    def wrap_raw_feature(self, feature: FTR):
        return PointFeature(feature)
