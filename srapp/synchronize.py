import typing
import traceback
from typing import List

from google.cloud.firestore_v1.client import Client
from google.cloud.firestore_v1.watch import ChangeType
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from qgis._core import (QgsFeature, QgsVectorLayer, QgsMessageLog,
                        QgsFeatureRequest, QgsExpression)

from .database.point import Point
from .database import point
from .database.borehole import BoreholeProduct
from .database.layer import Layer
from .database.shear import Shear
from .database.probe import ProbeProduct
from .database.water import DrilledWaterHorizon, SetWaterHorizon, Exudation
from .database.data import Data
from . import project


class Synchronizer:
    def __init__(self, email: str, client: Client, projects: List[project.Project]):
        self.email: str = email
        self.client: Client = client
        self.projects: List[project.Project] = projects
        self.watches = set()

    def synchronize(self):
        for p in self.projects:
            p.reset()
            watches = self._listen_to_project(p)
            if watches is not None:
                self.watches.update(watches)

    def _listen_to_project(self, p: project.Project):
        name: str = p.name
        project_ref = self.client.collection('users').document(self.email).collection('projects').document(name)
        map_points_ref = project_ref.collection('map_points')
        boreholes_ref = project_ref.collection('boreholes')
        probes_ref = project_ref.collection('probes')

        try:
            points_watch = _listen_points_changes(map_points_ref, p)
            boreholes_watch = _listen_boreholes_changes(boreholes_ref, p)
            probes_watch = _listen_probes_changes(probes_ref, p)
        except Exception as e:
            raise e
        return {points_watch, boreholes_watch, probes_watch}

    def desynchronize(self):
        if self.watches:
            for watch in self.watches:
                watch.unsubscribe()


def _listen_points_changes(map_points_ref, p: project.Project):
    def on_map_points(changes):
        points_layer: QgsVectorLayer = p.points_layer
        shears_layer: QgsVectorLayer = p.shears_todo_layer

        for change in changes:
            change_type = change.type
            doc = change.document
            point: Point = Point.from_dict(doc.to_dict())
            if not point:
                continue
            shears: [] = point.shearsToDoList
            point_name = point.pointNumber

            if change_type == ChangeType.REMOVED:
                _delete_feature(points_layer, point_name)
                _delete_all_features(shears_layer, point_name)
            elif change_type == ChangeType.ADDED:
                _add_feature(points_layer, point.attr_map, point.to_feature, point_name)
                _add_features(shears, shears_layer, point_name)
            elif change_type == ChangeType.MODIFIED:
                _add_feature(points_layer, point.attr_map, point.to_feature, point_name)
                _add_features(shears, shears_layer, point_name)
            QgsMessageLog.logMessage(f'{change_type} {doc.id}', 'SRApp - punkty')
        points_layer.updateExtents()

    def on_map_points_snapshot(doc_snapshot, changes, read_time):
        _on_iteration(on_map_points, changes)

    return map_points_ref.on_snapshot(on_map_points_snapshot)


def _on_iteration(func: callable, changes):
    try:
        func(changes)
    except Exception as e:
        QgsMessageLog.logMessage(f'{traceback.format_exc()}', 'SRApp - błąd')
        raise e


def _listen_boreholes_changes(boreholes_ref, p: project.Project):
    def on_boreholes(changes):
        boreholes_layer: QgsVectorLayer = p.boreholes_layer
        layers_layer: QgsVectorLayer = p.layers_layer
        drilled_water_layer: QgsVectorLayer = p.drilled_water_horizons_layer
        set_water_layer: QgsVectorLayer = p.set_water_horizons_layer
        exudations_layer: QgsVectorLayer = p.exudations_layer
        additional_layers = [layers_layer, drilled_water_layer, set_water_layer, exudations_layer]

        for change in changes:
            change_type = change.type
            doc: DocumentSnapshot = change.document
            bp: BoreholeProduct = BoreholeProduct.from_dict(doc.to_dict())
            layers: List[Layer] = bp.layers
            drilled_water_list: List[DrilledWaterHorizon] = bp.drilledWaterHorizons
            set_water_list: List[SetWaterHorizon] = bp.setWaterHorizons
            exudations: List[Exudation] = bp.exudations
            additional_lists = [layers, drilled_water_list, set_water_list, exudations]
            additional = zip(additional_layers, additional_lists)
            point_name = bp.name

            if change_type == ChangeType.REMOVED:
                _delete_feature(boreholes_layer, point_name)
                for add in additional:
                    _delete_all_features(add[0], point_name)
            elif change_type == ChangeType.ADDED:
                _add_feature(boreholes_layer, bp.attr_map, bp.to_feature, point_name)
                for add in additional:
                    _add_features(add[1], add[0], point_name)
            elif change_type == ChangeType.MODIFIED:
                _add_feature(boreholes_layer, bp.attr_map, bp.to_feature, point_name)
                for add in additional:
                    _add_features(add[1], add[0], point_name)
            QgsMessageLog.logMessage(f'{change_type} {doc.id}', 'SRApp - wiercenia')

    def on_boreholes_snapshot(doc_snapshot, changes, read_time):
        return _on_iteration(on_boreholes, changes)

    return boreholes_ref.on_snapshot(on_boreholes_snapshot)


def _listen_probes_changes(probes_ref, p: project.Project):
    def on_probes(changes):
        probes_layer: QgsVectorLayer = p.probes_layer
        shears_layer: QgsVectorLayer = p.shears_layer

        for change in changes:
            change_type = change.type
            doc: DocumentSnapshot = change.document
            pp: ProbeProduct = ProbeProduct.from_dict(doc.to_dict())
            shears: List[Shear] = pp.shears
            point_name = pp.name

            if change_type == ChangeType.REMOVED:
                _delete_feature(probes_layer, point_name)
                _delete_all_features(shears_layer, point_name)
            elif change_type == ChangeType.ADDED:
                _add_feature(probes_layer, pp.attr_map, pp.to_feature, point_name)
                _add_features(shears, shears_layer, point_name)
            elif change_type == ChangeType.MODIFIED:
                _add_feature(probes_layer, pp.attr_map, pp.to_feature, point_name)
                _add_features(shears, shears_layer, point_name)
            QgsMessageLog.logMessage(f'{change_type} {doc.id}', 'SRApp - sondowania')

    def on_probes_snapshot(doc_snapshot, changes, read_time):
        return _on_iteration(on_probes, changes)

    return probes_ref.on_snapshot(on_probes_snapshot)


def _get_features(name: str, layer: QgsVectorLayer) -> typing.List[QgsFeature]:
    expression = QgsExpression(f'"{point.NAME}"=\'{name}\'')
    features = layer.getFeatures(QgsFeatureRequest(expression))
    return list(features) if features else []


def _get_feature(name: str, layer) -> QgsFeature:
    features: [] = _get_features(name, layer)
    if len(features) > 1:
        # todo action when more than one item is returned when should be unique
        pass
    return features[0] if features else None


def _delete_feature(layer: QgsVectorLayer, point_name):
    provider = layer.dataProvider()
    feat = _get_feature(point_name, layer)
    if feat:
        provider.deleteFeatures([feat.id()])


def _delete_all_features(layer: QgsVectorLayer, point_name):
    provider = layer.dataProvider()
    layer_features = _get_features(point_name, layer)
    if layer_features:
        provider.deleteFeatures([feat.id() for feat in layer_features])


def _add_feature(layer: QgsVectorLayer, attr_map_getter: callable, feature_getter: callable, point_name):
    provider = layer.dataProvider()
    feat = _get_feature(point_name, layer)
    if feat:
        attr_map = attr_map_getter(feat.id())
        provider.changeAttributeValues(attr_map)
    else:
        new_feat = feature_getter()
        provider.addFeature(new_feat)


def _add_features(items: List[Data], qgs_layer: QgsVectorLayer, point_name: str):
    features = _get_features(point_name, qgs_layer)
    rows = max(len(items), len(features))
    pos_with_feat_and_layer = {
        i: [
            features[i] if len(features) > i else None,
            items[i] if len(items) > i else None
        ]
        for i in range(rows)
    }
    provider = qgs_layer.dataProvider()
    for idx, feat_and_item in pos_with_feat_and_layer.items():
        feat = feat_and_item[0]
        item = feat_and_item[1]
        if feat and item:
            attr_map = item.attr_map(feat.id())
            provider.changeAttributeValues(attr_map)
        elif feat:
            provider.deleteFeatures([feat.id()])
        elif item:
            provider.addFeature(item.to_feature())
