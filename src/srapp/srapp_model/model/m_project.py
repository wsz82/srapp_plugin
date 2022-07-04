import abc
import datetime
import enum
import os
from typing import *

import database.borehole
import model.m_user
from database import data, person, product_point, team, constants
from database.data import IFeature, IPointFeature
from model.m_config import SHEARS_TODO_LAYER_STR, BOREHOLES_LAYER_STR, BOREHOLE_PERSONS_LAYER_STR, LAYERS_LAYER_STR, \
    DRILLED_WATER_LAYER_STR, SET_WATER_LAYER_STR, EXUDATIONS_LAYER_STR, PROBES_LAYER_STR, PROBE_UNITS_LAYER_STR, \
    PROBE_PERSONS_LAYER_STR, SHEAR_UNITS_LAYER_STR, TEAMS_LAYER_STR, POINTS_LAYER_STR
from model.m_layer import IMapLayer
from srapp_model.database import point
from srapp_model.database import shear, borehole, probe, layer, water


class FieldType(enum.Enum):
    STRING = 1
    DOUBLE = 2
    BOOL = 3
    INT = 4
    DATETIME = 5


FLD = TypeVar('FLD')


class IFieldCreator(Generic[FLD]):

    @abc.abstractmethod
    def make_field(self, constraints=None, **kwargs) -> FLD:
        return

    @abc.abstractmethod
    def get_field_type(self, field_type: FieldType) -> Any:
        return


def points_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = point.LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Czas', type=f_type(FieldType.DATETIME)))
    fields.append(make(name=names.pop(0), comment='Nazwa', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Twórca', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Wysokość', type=f_type(FieldType.DOUBLE), prec=2))
    fields.append(make(name=names.pop(0), comment='Układ wysokości', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Stan wiercenia', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Stan sondowania', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Projektowana gł. wiercenia', type=f_type(FieldType.DOUBLE), prec=2))
    fields.append(make(name=names.pop(0), comment='Projektowana gł. sondowania', type=f_type(FieldType.DOUBLE), prec=2))
    fields.append(make(name=names.pop(0), comment='Czy wytyczone', type=f_type(FieldType.BOOL)))
    fields.append(make(name=names.pop(0), comment='Typ sondowania', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Właściciel', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Kontakt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Przypisany wykonawca', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Komentarz', type=f_type(FieldType.STRING)))
    return fields


def boreholes_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = borehole.LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Czas', type=f_type(FieldType.DATETIME)))
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Ostatni wykonwaca', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Lokacja', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Nr. rejestracyjny pojazdu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Głębokość początkowa', type=f_type(FieldType.DOUBLE), prec=2))
    fields.append(make(name=names.pop(0), comment='Typ wiercenia', type=f_type(FieldType.STRING)))
    return fields


def shears_todo_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = shear.SHEAR_TODO_LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Głębokość ścięcia', type=f_type(FieldType.DOUBLE), prec=2))
    return fields


def layers_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = layer.LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Przelot', type=f_type(FieldType.DOUBLE), prec=2))
    fields.append(make(name=names.pop(0), comment='Rodzaj gruntu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Domieszki gruntu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Przewarstwienia gruntu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Kolor gruntu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Wilgotność gruntu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Ilość wałeczkowań', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Stan gruntu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Opróbowanie', type=f_type(FieldType.DOUBLE), prec=2))
    fields.append(make(name=names.pop(0), comment='Opis gruntu', type=f_type(FieldType.STRING)))
    return fields


def drilled_water_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = water.DRILLED_WATER_LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Warstwa wodonośna', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Głębokość zwierciadłą', type=f_type(FieldType.DOUBLE)))
    fields.append(make(name=names.pop(0), comment='Czas', type=f_type(FieldType.DATETIME)))
    return fields


def set_water_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = water.SET_WATER_LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Warstwa wodonośna', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Głębokość zwierciadłą', type=f_type(FieldType.DOUBLE)))
    fields.append(make(name=names.pop(0), comment='Czas', type=f_type(FieldType.DATETIME)))
    fields.append(make(name=names.pop(0), comment='Okres pomiaru po odwiercie [min]', type=f_type(FieldType.INT)))
    return fields


def exudations_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = water.EXUDATION_LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Wielkość sączenia (1-3)', type=f_type(FieldType.INT)))
    fields.append(make(name=names.pop(0), comment='Głębokość', type=f_type(FieldType.DOUBLE)))
    fields.append(make(name=names.pop(0), comment='Czas', type=f_type(FieldType.DATETIME)))
    return fields


def probes_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = probe.LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Czas', type=f_type(FieldType.DATETIME)))
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Ostatni wykonwaca', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Lokacja', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Nr. rejestracyjny pojazdu', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Głębokość początkowa', type=f_type(FieldType.DOUBLE), prec=2))
    fields.append(make(name=names.pop(0), comment='Typ sondowania', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Interwał', type=f_type(FieldType.DOUBLE)))
    return fields


def persons_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = person.LOCAL_TO_REMOTE.local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Wykonawca', type=f_type(FieldType.STRING)))
    return fields


def shear_unit_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = shear.shear_unit_local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Głebokość ścięcia', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Liczba porządkowa', type=f_type(FieldType.INT)))
    fields.append(make(name=names.pop(0), comment='Wartość', type=f_type(FieldType.INT)))
    return fields


def probe_unit_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = probe.probe_unit_local_names()
    fields.append(make(name=names.pop(0), comment='Punkt', type=f_type(FieldType.STRING)))
    fields.append(make(name=names.pop(0), comment='Liczba porządkowa', type=f_type(FieldType.INT)))
    fields.append(make(name=names.pop(0), comment='Wartość', type=f_type(FieldType.INT)))
    return fields


def teams_fields(creator: IFieldCreator) -> List[FLD]:
    make = creator.make_field
    f_type = creator.get_field_type
    fields = []
    names = team.team_local_names()
    fields.append(make(name=names.pop(0), comment='Czas', type=f_type(FieldType.DATETIME)))
    fields.append(make(name=names.pop(0), comment='Nazwa', type=f_type(FieldType.STRING)))
    return fields


def _persons_list_map(features: List[IFeature]) -> dict:
    elements = []
    for feat in features:
        element = str(feat.attribute(data.PERSON) or '')
        if not element:
            continue
        assert type(element) is str
        elements.append(element)
    data_map = {
        product_point.REMOTE_POINT: {
            person.REMOTE_PERSONS: elements
        }
    }
    return data_map


def _probe_units_list_map(features: List[IFeature]) -> dict:
    def sorter(feat: IFeature) -> int:
        idx = feat.attribute(shear.INDEX)
        assert type(idx) is int
        return idx

    features.sort(key=sorter)
    elements = []
    for feat in features:
        element = str(feat.attribute(probe.VALUE) or '')
        assert type(element) is str
        elements.append(element)
    data_map = {
        probe.REMOTE_PROBE: {
            probe.UNITS_REMOTE: elements
        }
    }
    return data_map


def _shear_units_list_map(features: List[IFeature]) -> dict:
    depths_set = {_round_depth(float(f.attribute(shear.SHEAR_DEPTH) or 0)) for f in features}
    shears = []

    def sorter(feat: IFeature) -> int:
        idx = feat.attribute(shear.INDEX)
        assert type(idx) is int
        return idx

    for depth in depths_set:
        assert type(depth) is float
        depth_features = [f for f in features if f.attribute(shear.SHEAR_DEPTH) == depth]
        depth_features.sort(key=sorter)
        shears_torques = [f.attribute(shear.VALUE) for f in depth_features]
        for t in shears_torques:
            assert type(t) is str
        shear_map = {
            shear.SHEAR_DEPTH_REMOTE: str(depth),
            shear.TORQUES_REMOTE: shears_torques
        }
        shears.append(shear_map)
    data_map = {
        shear.SHEARS_REMOTE: shears
    }
    return data_map


def _water_horizons_map(features: List[IFeature]) -> dict:
    horizons_list = []
    for feat in features:
        horizon_value = str(feat.attribute(water.HORIZON))
        assert type(horizon_value) is str
        water_depth = str(_round_depth(float(feat.attribute(water.WATER_DEPTH) or 0)))
        assert type(water_depth) is str
        time = _make_time(feat)
        horizons_list.append({
            water.REMOTE_DATA: horizon_value,
            water.WATER_DEPTH_REMOTE: water_depth,
            water.TIME_REMOTE: time,
        })
    data_map = {
        database.borehole.DRILLED_WATER_HORIZONS_REMOTE: horizons_list
    }
    return data_map


def _exudations_list(features: List[IFeature]) -> dict:
    exudations_list = []
    for feat in features:
        exudation_type = str(feat.attribute(water.EXUDATION_TYPE) or '')
        assert type(exudation_type) is str
        depth_value = str(_round_depth(float(feat.attribute(water.EXUDATION_DEPTH) or 0)))
        assert type(depth_value) is str
        time = _make_time(feat)
        exudations_list.append({
            water.REMOTE_DATA: exudation_type,
            water.WATER_DEPTH_REMOTE: depth_value,
            water.TIME_REMOTE: time,
        })
    data_map = {
        database.borehole.EXUDATIONS_REMOTE: exudations_list
    }
    return data_map


def _layers_map(features: List[IFeature]) -> dict:
    layers_list = []
    for feat in features:
        to = str(_round_depth(float(feat.attribute(layer.TO) or 0)))
        assert type(to) is str
        soil_type = feat.attribute(layer.TYPE) or ''
        assert type(soil_type) is str
        admixtures = feat.attribute(layer.ADMIXTURES) or ''
        assert type(admixtures) is str
        interbeddings = feat.attribute(layer.INTERBEDDINGS) or ''
        assert type(interbeddings) is str
        color = feat.attribute(layer.COLOR) or ''
        assert type(color) is str
        moisture = feat.attribute(layer.MOISTURE) or ''
        assert type(moisture) is str
        rolls_number = feat.attribute(layer.ROLLS_NUMBER) or ''
        assert type(rolls_number) is str
        soil_state = feat.attribute(layer.SOIL_STATE) or ''
        assert type(soil_state) is str
        sampling = str(feat.attribute(layer.SAMPLING) or '')
        assert type(sampling) is str
        description = feat.attribute(layer.DESCRIPTION) or ''
        assert type(description) is str
        layers_list.append({
            layer.TO_REMOTE: to,
            layer.TYPE_REMOTE: soil_type,
            layer.ADMIXTURES_REMOTE: admixtures,
            layer.INTERBEDDINGS_REMOTE: interbeddings,
            layer.COLOR_REMOTE: color,
            layer.MOISTURE_REMOTE: moisture,
            layer.ROLLS_NUMBER_REMOTE: rolls_number,
            layer.SOIL_STATE_REMOTE: soil_state,
            layer.SAMPLING_REMOTE: sampling,
            layer.DESCRIPTION_REMOTE: description,
        })
    data_map = {
        database.borehole.LAYERS_REMOTE: layers_list
    }
    return data_map


def _todo_shears_list(features: List[IFeature]) -> dict:
    todo_shears_list = []
    for feat in features:
        shear_depth = _round_depth(float(feat.attribute(shear.SHEAR_DEPTH) or 0))
        assert type(shear_depth) is float
        todo_shears_list.append(shear_depth)
    data_map = {
        point.SHEARS_TODO_LIST_REMOTE: todo_shears_list
    }
    return data_map


def _points_map(features: List[IPointFeature]) -> dict:
    data_map = {}
    for feature in features:
        borehole_depth: str = str(_round_depth(float(feature.attribute(point.BOREHOLE_DEPTH) or 0)))
        assert type(borehole_depth) is str
        probe_depth: str = str(_round_depth(float(feature.attribute(point.PROBE_DEPTH) or 0)))
        assert type(probe_depth) is str
        name = _make_name(feature)
        height: float = _round_depth(float(feature.attribute(point.HEIGHT) or 0))
        assert type(height) is float
        stakeout: bool = feature.attribute(point.STAKEOUT) or False
        assert type(stakeout) is bool
        creator: str = feature.attribute(point.CREATOR) or ''
        assert type(creator) is str
        height_system: str = feature.attribute(point.HEIGHT_SYSTEM) or ''
        assert type(height_system) is str
        borehole_state: str = feature.attribute(point.BOREHOLE_STATE) or ''
        borehole_state = constants.STATUSES_REMOTE_TO_LOCAL.key(borehole_state)
        assert type(borehole_state) is str
        probe_state: str = feature.attribute(point.PROBE_STATE) or ''
        probe_state = constants.STATUSES_REMOTE_TO_LOCAL.key(probe_state)
        assert type(probe_state) is str
        probe_type: str = feature.attribute(point.PROBE_TYPE) or ''
        assert type(probe_type) is str
        owner: str = feature.attribute(point.OWNER) or ''
        assert type(owner) is str
        contact: str = feature.attribute(point.CONTACT) or ''
        assert type(contact) is str
        assigned_performer: str = feature.attribute(point.ASSIGNED_PERFORMER) or ''
        assert type(assigned_performer) is str
        comments: str = feature.attribute(point.COMMENTS) or ''
        assert type(comments) is str
        time = _make_time(feature)
        point_map = {
            data.TIME_REMOTE: time,
            data.NAME_REMOTE: name,
            point.CREATOR_REMOTE: creator,
            point.HEIGHT_REMOTE: height,
            point.HEIGHT_SYSTEM_REMOTE: height_system,
            point.BOREHOLE_STATE_REMOTE: borehole_state,
            point.PROBE_STATE_REMOTE: probe_state,
            point.BOREHOLE_DEPTH_REMOTE: borehole_depth,
            point.PROBE_DEPTH_REMOTE: probe_depth,
            point.STAKEOUT_REMOTE: stakeout,
            point.PROBE_TYPE_REMOTE: probe_type,
            point.OWNER_REMOTE: owner,
            point.CONTACT_REMOTE: contact,
            point.ASSIGNED_PERFORMER_REMOTE: assigned_performer,
            point.COMMENTS_REMOTE: comments,
        }
        x, y = feature.xy()
        point_map.update({
            point.POINT_X: x,
            point.POINT_Y: y
        })
        data_map.update({name: point_map})
    return data_map


def _boreholes_map(features: List[IFeature]) -> dict:
    data_map = {}
    for feature in features:
        name, borehole_map = _product_point_map(feature)
        drill_type = str(feature.attribute(product_point.TYPE) or '')
        assert type(drill_type) is str
        borehole_map.update({
            borehole.REMOTE_DRILL_TYPE: drill_type,
        })
        borehole_map = borehole.remote_transformation(borehole_map)
        data_map.update({name: borehole_map})
    return data_map


def _probes_map(features: List[IFeature]) -> dict:
    data_map = {}
    for feature in features:
        name, probe_map = _product_point_map(feature)
        drill_type = str(feature.attribute(product_point.TYPE) or '')
        assert type(drill_type) is str
        probe_type = str(feature.attribute(probe.PROBE_TYPE) or '')
        assert type(probe_type) is str
        interval = float(feature.attribute(probe.INTERVAL) or constants.DEFAULT_PROBE_INTERVAL)
        assert type(interval) is float
        probe_map.update({
            probe.PROBE_TYPE_REMOTE: probe_type,
            probe.INTERVAL_REMOTE: interval,
        })
        probe_map = probe.remote_transformation(probe_map)
        data_map.update({name: probe_map})
    return data_map


def _product_point_map(feature):
    time = _make_time(feature)
    name = _make_name(feature)
    last_performer = str(feature.attribute(product_point.LAST_PERFORMER) or '')
    assert type(last_performer) is str
    location = str(feature.attribute(product_point.LOCATION) or '')
    assert type(location) is str
    vehicle_number = str(feature.attribute(product_point.VEHICLE_NUMBER) or '')
    assert type(vehicle_number) is str
    start_depth = _round_depth(float(feature.attribute(product_point.START_DEPTH) or 0))
    assert type(start_depth) is float
    point_map = {
        data.TIME_REMOTE: time,
        data.NAME_REMOTE: name,
        product_point.LAST_PERFORMER_REMOTE: last_performer,
        product_point.LOCATION_REMOTE: location,
        product_point.VEHICLE_NUMBER_REMOTE: vehicle_number,
        product_point.START_DEPTH_REMOTE: start_depth,
    }
    return name, point_map


def _round_depth(depth: float):
    return round(depth, 2)


def _make_name(feature):
    name = str(feature.attribute(data.NAME))
    assert type(name) is str
    return name


def _make_time(feature: IFeature) -> datetime.datetime:
    time = feature.time() or datetime.datetime.utcnow()
    assert isinstance(time, datetime.datetime)
    return time


def _team_map(features: List[IFeature]) -> dict:
    data_map = {}
    for feature in features:
        time = _make_time(feature)
        name = _make_name(feature)
        time_map = {
            data.TIME_REMOTE: time,
            data.NAME_REMOTE: name,
        }
        data_map.update({name: time_map})
    return data_map


class Project:
    def __init__(self, name: str, projects_dir: str, **layers):
        self._name: str = name
        self._dir: str = projects_dir
        self._gpkg_file_path: str = os.path.join(self.dir, f'{name}.gpkg')
        self.set_layers(**layers)
        self._layers_names = [
            POINTS_LAYER_STR,
            SHEARS_TODO_LAYER_STR,
            BOREHOLES_LAYER_STR,
            BOREHOLE_PERSONS_LAYER_STR,
            LAYERS_LAYER_STR,
            DRILLED_WATER_LAYER_STR,
            SET_WATER_LAYER_STR,
            EXUDATIONS_LAYER_STR,
            PROBES_LAYER_STR,
            PROBE_UNITS_LAYER_STR,
            PROBE_PERSONS_LAYER_STR,
            SHEAR_UNITS_LAYER_STR,
            TEAMS_LAYER_STR,
        ]

    @property
    def layers_names(self):
        return self._layers_names

    @property
    def name(self):
        return self._name

    @property
    def dir(self):
        return self._dir

    @property
    def gpkg_file_path(self):
        return self._gpkg_file_path

    def set_layers(self, **layers):
        points_ref = model.m_user.POINTS_REMOTE
        boreholes_ref = model.m_user.BOREHOLES_REMOTE
        probes_ref = model.m_user.PROBES_REMOTE
        teams_ref = model.m_user.TEAMS_REMOTE

        self.layers: List[IMapLayer] = list(layers.values())
        [l.set_project(self) for l in self.layers]

        self.points_layer: IMapLayer = layers.get(POINTS_LAYER_STR)
        if self.points_layer:
            self.points_layer.name = POINTS_LAYER_STR
            self.points_layer.can_make_timestamp_on_added = True
            self.points_layer.database_ref_path = points_ref
            self.points_layer.features_to_remote = _points_map
            self.points_layer.local_to_remote = point.LOCAL_TO_REMOTE

        self.boreholes_layer: IMapLayer = layers.get(BOREHOLES_LAYER_STR)
        if self.boreholes_layer:
            self.boreholes_layer.name = BOREHOLES_LAYER_STR
            self.boreholes_layer.can_make_timestamp_on_added = True
            self.boreholes_layer.database_ref_path = boreholes_ref
            self.boreholes_layer.features_to_remote = _boreholes_map
            self.boreholes_layer.remote_transformation = borehole.remote_transformation
            self.boreholes_layer.local_to_remote = borehole.LOCAL_TO_REMOTE

        self.probes_layer: IMapLayer = layers.get(PROBES_LAYER_STR)
        if self.probes_layer:
            self.probes_layer.name = PROBES_LAYER_STR
            self.probes_layer.can_make_timestamp_on_added = True
            self.probes_layer.database_ref_path = probes_ref
            self.probes_layer.features_to_remote = _probes_map
            self.probes_layer.remote_transformation = probe.remote_transformation
            self.probes_layer.local_to_remote = probe.LOCAL_TO_REMOTE

        self.borehole_persons_layer: IMapLayer = layers.get(BOREHOLE_PERSONS_LAYER_STR)
        if self.borehole_persons_layer:
            self.borehole_persons_layer.name = BOREHOLE_PERSONS_LAYER_STR
            self.borehole_persons_layer.database_ref_path = boreholes_ref
            self.borehole_persons_layer.features_to_remote = _persons_list_map

        self.shears_todo_layer: IMapLayer = layers.get(SHEARS_TODO_LAYER_STR)
        if self.shears_todo_layer:
            self.shears_todo_layer.name = SHEARS_TODO_LAYER_STR
            self.shears_todo_layer.database_ref_path = points_ref
            self.shears_todo_layer.features_to_remote = _todo_shears_list

        self.layers_layer: IMapLayer = layers.get(LAYERS_LAYER_STR)
        if self.layers_layer:
            self.layers_layer.name = LAYERS_LAYER_STR
            self.layers_layer.database_ref_path = boreholes_ref
            self.layers_layer.features_to_remote = _layers_map

        self.drilled_water_horizons_layer: IMapLayer = layers.get(DRILLED_WATER_LAYER_STR)
        if self.drilled_water_horizons_layer:
            self.drilled_water_horizons_layer.name = DRILLED_WATER_LAYER_STR
            self.drilled_water_horizons_layer.database_ref_path = boreholes_ref
            self.drilled_water_horizons_layer.features_to_remote = _water_horizons_map

        self.set_water_horizons_layer: IMapLayer = layers.get(SET_WATER_LAYER_STR)
        if self.set_water_horizons_layer:
            self.set_water_horizons_layer.name = SET_WATER_LAYER_STR
            self.set_water_horizons_layer.database_ref_path = boreholes_ref
            self.set_water_horizons_layer.features_to_remote = _water_horizons_map

        self.exudations_layer: IMapLayer = layers.get(EXUDATIONS_LAYER_STR)
        if self.exudations_layer:
            self.exudations_layer.name = EXUDATIONS_LAYER_STR
            self.exudations_layer.database_ref_path = boreholes_ref
            self.exudations_layer.features_to_remote = _exudations_list

        self.probe_persons_layer: IMapLayer = layers.get(PROBE_PERSONS_LAYER_STR)
        if self.probe_persons_layer:
            self.probe_persons_layer.name = PROBE_PERSONS_LAYER_STR
            self.probe_persons_layer.database_ref_path = probes_ref
            self.probe_persons_layer.features_to_remote = _persons_list_map

        self.probe_units_layer: IMapLayer = layers.get(PROBE_UNITS_LAYER_STR)
        if self.probe_units_layer:
            self.probe_units_layer.name = PROBE_UNITS_LAYER_STR
            self.probe_units_layer.database_ref_path = probes_ref
            self.probe_units_layer.features_to_remote = _probe_units_list_map

        self.shear_units_layer: IMapLayer = layers.get(SHEAR_UNITS_LAYER_STR)
        if self.shear_units_layer:
            self.shear_units_layer.name = SHEAR_UNITS_LAYER_STR
            self.shear_units_layer.database_ref_path = probes_ref
            self.shear_units_layer.features_to_remote = _shear_units_list_map

        self.teams_layer: IMapLayer = layers.get(TEAMS_LAYER_STR)
        if self.teams_layer:
            self.teams_layer.name = TEAMS_LAYER_STR
            self.teams_layer.database_ref_path = teams_ref
            self.teams_layer.features_to_remote = _team_map

    def reset(self):
        [layer.delete_all_features() for layer in self.layers]

    def layer_by_id(self, layer_id: str) -> 'IMapLayer':
        layers = [l for l in self.layers if l.id() == layer_id]
        assert len(layers) == 1
        return layers[0]
