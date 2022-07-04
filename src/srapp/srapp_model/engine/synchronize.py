import abc
import traceback
from typing import *

from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.cloud.firestore_v1.watch import ChangeType, Watch

from database.data import Data, IFeature
from database.person import Person
from database.team import TeamPoint
from model.m_layer import IListener, IMapLayer
from model.m_qgis import IQgis
from model.m_user import User
from remote import remote_update
from srapp_model import G
from srapp_model.database import data
from srapp_model.database.borehole import BoreholeProduct
from srapp_model.database.layer import Layer
from srapp_model.database.point import Point
from srapp_model.database.probe import ProbeProduct
from srapp_model.database.shear import ShearUnit
from srapp_model.database.water import DrilledWaterHorizon, SetWaterHorizon, Exudation
from srapp_model.model.m_project import Project


class ListenerWatch(IListener[Watch]):

    @abc.abstractmethod
    def stop(self):
        self.obj.unsubscribe()


class Synchronizer:
    def __init__(self, qgis: IQgis, user: User, projects: List[Project]):
        self.qgis: IQgis = qgis
        self.user: User = user
        self.projects: List[Project] = projects
        for p in self.projects:
            for layer in p.layers:
                layer.set_editable(True)
        self._listeners: List[IListener] = []

    def synchronize(self):
        for project in self.projects:
            # todo not reseting means leaving the data that not exists in remote
            # project.reset()
            for layer in project.layers:
                features = layer.all_features()
                layer.fid_to_name.update({f.fid(): f.name() for f in features})
            self._listen_to_remote(project)

    def desynchronize(self):
        for p in self.projects:
            for layer in p.layers:
                layer.stop_edit_mode()
                layer.set_editable(False)
        for listener in self._listeners:
            listener.stop()
        self._listeners.clear()

    def _listen_to_remote(self, project: Project):
        map_points_ref = self.user.map_points_ref(project.name)
        boreholes_ref = self.user.boreholes_ref(project.name)
        probes_ref = self.user.probes_ref(project.name)
        teams_ref = self.user.teams_ref(project.name)
        try:
            if project.points_layer:
                self._listeners.append(self._listen_points_changes(map_points_ref, project))
                self._listen_to_layer_changes(project.points_layer)
            if project.boreholes_layer:
                self._listeners.append(self._listen_boreholes_changes(boreholes_ref, project))
                self._listen_to_layer_changes(project.boreholes_layer)
            if project.probes_layer:
                self._listeners.append(self._listen_probes_changes(probes_ref, project))
                self._listen_to_layer_changes(project.probes_layer)
            if project.teams_layer:
                self._listeners.append(self._listen_team_changes(teams_ref, project))
                self._listen_to_layer_changes(project.teams_layer)

            self._listen_to_sublayer_changes(project.shears_todo_layer)
            self._listen_to_sublayer_changes(project.borehole_persons_layer)
            self._listen_to_sublayer_changes(project.layers_layer)
            self._listen_to_sublayer_changes(project.drilled_water_horizons_layer)
            self._listen_to_sublayer_changes(project.set_water_horizons_layer)
            self._listen_to_sublayer_changes(project.exudations_layer)
            self._listen_to_sublayer_changes(project.probe_persons_layer)
            self._listen_to_sublayer_changes(project.probe_units_layer)
            self._listen_to_sublayer_changes(project.shear_units_layer)
        except Exception as e:
            self.desynchronize()
            raise e

    def _listen_to_layer_changes(self, layer: IMapLayer):
        if not layer:
            return
        self._listeners.append(layer.committed_features_added(self._on_items_added))
        self._listeners.append(layer.committed_features_removed(self._on_items_deleted))
        self._listeners.append(layer.committed_attribute_values_changes(self._on_items_changed))

    def _listen_to_sublayer_changes(self, layer: IMapLayer):
        if not layer:
            return
        self._listeners.append(layer.committed_features_added(self._on_subitems_added))
        self._listeners.append(layer.committed_features_removed(self._on_subitems_deleted))
        self._listeners.append(layer.committed_attribute_values_changes(self._on_subitems_changed))

    def project_layer_ref(self, layer: IMapLayer):
        project: Project = layer.project
        project_ref = self.user.project_ref(project.name)
        return project, project_ref

    def _on_items_added(self, layer: IMapLayer, features: Iterable[IFeature]):
        project, project_ref = self.project_layer_ref(layer)
        layer.fid_to_name.update({f.fid(): f.name() for f in features})
        names = {f.name() for f in features}
        remote_update.on_items_modify(project_ref, names, layer)

    def _on_items_deleted(self, layer: IMapLayer, deleted_features_fids: List[int]):
        project, project_ref = self.project_layer_ref(layer)
        collection_ref = project_ref.collection(layer.database_ref_path)
        names = {layer.fid_to_name.get(fid) for fid in deleted_features_fids}
        remote_update.on_items_deleted(collection_ref, names, layer.name)

    def _on_items_changed(self, layer: IMapLayer, features: List[IFeature]):
        project, project_ref = self.project_layer_ref(layer)
        names = {f.name() for f in features}
        remote_update.on_items_modify(project_ref, names, layer)

    def _on_subitems_added(self, layer: IMapLayer, features: List[IFeature]):
        project, project_ref = self.project_layer_ref(layer)
        names = {feat.name() for feat in features}
        layer.fid_to_name.update({f.fid(): f.name() for f in features})
        remote_update.on_subitems_modify(project_ref, names, layer)

    def _on_subitems_deleted(self, layer: IMapLayer, deleted_features_fids: List[int]):
        project, project_ref = self.project_layer_ref(layer)
        names = {layer.fid_to_name.get(fid) for fid in deleted_features_fids}
        remote_update.on_subitems_modify(project_ref, names, layer)

    def _on_subitems_changed(self, layer: IMapLayer, features: List[IFeature]):
        project, project_ref = self.project_layer_ref(layer)
        names = {f.name() for f in features}
        remote_update.on_subitems_modify(project_ref, names, layer)

    def _listen_points_changes(self, map_points_ref, project: Project) -> ListenerWatch:
        points_layer = project.points_layer
        shears_layer = project.shears_todo_layer

        def on_map_points(change_type, doc_map: dict):
            point: Point = Point.from_dict(doc_map)
            if not point:
                return
            shears: [] = point.shears_todo
            point_name = point.fields.get(data.NAME)

            if change_type == ChangeType.REMOVED:
                points_layer.delete_features_by_name(point_name)
                shears_layer.delete_features_by_name(point_name)
            elif change_type == ChangeType.ADDED or change_type == ChangeType.MODIFIED:
                points_layer.add_feature(point, point_name)
                shears_layer.add_features(shears, point_name)

        def on_map_points_snapshot(doc_snapshot, changes, read_time):
            _on_iteration(points_layer, 'punkty', on_map_points, changes)
            points_layer.refresh()

        return ListenerWatch(map_points_ref.on_snapshot(on_map_points_snapshot))

    def _listen_boreholes_changes(self, boreholes_ref, p: Project) -> ListenerWatch:
        boreholes_layer = p.boreholes_layer
        persons_layer = p.borehole_persons_layer
        layers_layer = p.layers_layer
        drilled_water_layer = p.drilled_water_horizons_layer
        set_water_layer = p.set_water_horizons_layer
        exudations_layer = p.exudations_layer
        additional_layers = [persons_layer, layers_layer, drilled_water_layer, set_water_layer, exudations_layer]

        def on_boreholes(change_type, doc_map: dict):
            bp: BoreholeProduct = BoreholeProduct.from_dict(doc_map)
            persons: List[Person] = bp.borehole.persons
            layers: List[Layer] = bp.layers
            drilled_water_list: List[DrilledWaterHorizon] = bp.drilledWaterHorizons
            set_water_list: List[SetWaterHorizon] = bp.setWaterHorizons
            exudations: List[Exudation] = bp.exudations
            additional_lists = [persons, layers, drilled_water_list, set_water_list, exudations]
            additional = zip(additional_layers, additional_lists)
            point_name = bp.name

            if change_type == ChangeType.REMOVED:
                boreholes_layer.delete_features_by_name(point_name)
                for add in additional:
                    add[0].delete_features_by_name(point_name)
            elif change_type == ChangeType.ADDED or change_type == ChangeType.MODIFIED:
                boreholes_layer.add_feature(bp, point_name)
                for add in additional:
                    add[0].add_features(add[1], point_name)

        def on_boreholes_snapshot(doc_snapshot, changes, read_time):
            return _on_iteration(boreholes_layer, 'wiercenia', on_boreholes, changes)

        return ListenerWatch(boreholes_ref.on_snapshot(on_boreholes_snapshot))

    def _listen_probes_changes(self, probes_ref, p: Project) -> ListenerWatch:
        probes_layer = p.probes_layer
        probe_units_layer = p.probe_units_layer
        shears_layer = p.shear_units_layer
        persons_layer = p.probe_persons_layer

        def on_probes(change_type, doc_map: dict):
            pp: ProbeProduct = ProbeProduct.from_dict(doc_map)
            persons: List[Person] = pp.probe.persons
            shears: List[ShearUnit] = pp.shears
            point_name = pp.name

            if change_type == ChangeType.REMOVED:
                probes_layer.delete_features_by_name(point_name)
                probe_units_layer.delete_features_by_name(point_name)
                shears_layer.delete_features_by_name(point_name)
                persons_layer.delete_features_by_name(point_name)
            elif change_type == ChangeType.ADDED or change_type == ChangeType.MODIFIED:
                probes_layer.add_feature(pp, point_name)
                probe_units_layer.add_features(pp.probe.units, point_name)
                shears_layer.add_features(shears, point_name)
                persons_layer.add_features(persons, point_name)

        def on_probes_snapshot(doc_snapshot, changes, read_time):
            return _on_iteration(probes_layer, 'sondowania', on_probes, changes)

        return ListenerWatch(probes_ref.on_snapshot(on_probes_snapshot))

    def _listen_team_changes(self, teams_ref, p: Project) -> ListenerWatch:
        def on_teams_snapshot(doc_snapshots: List[DocumentSnapshot], changes, read_time):
            try:
                teams_layer = p.teams_layer
                for doc_snapshot in doc_snapshots:
                    team_doc = doc_snapshot.to_dict()
                    team: TeamPoint = TeamPoint.from_dict(team_doc)
                    teams_layer.add_feature(team, team.name)
                teams_layer.refresh()
            except Exception as e:
                G.Log.error(f'{traceback.format_exc()}')
                raise e

        return ListenerWatch(teams_ref.on_snapshot(on_teams_snapshot))


def _on_iteration(basic_layer: IMapLayer, tag: str, func: callable, changes):
    try:
        for change in changes:
            change_type = change.type
            doc: DocumentSnapshot = change.document
            doc_map = doc.to_dict()
            name = doc_map.get(data.NAME_REMOTE)
            if not name:
                continue
            feat = basic_layer.feature_by_name(name)
            if feat:
                local_time = str(feat.time())
                raw_remote_time = doc_map.get(data.TIME_REMOTE)
                remote_time = str(Data.remote_time_to_local(raw_remote_time))
                if local_time == remote_time:
                    continue

            func(change_type, doc_map)

            G.Log.message(f'{change_type} {doc.id}', f'SRApp - {tag}')
    except Exception as e:
        G.Log.error(f'{traceback.format_exc()}')
        raise e
