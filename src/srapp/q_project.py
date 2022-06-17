import os
from pathlib import Path
from typing import *

from qgis.PyQt.QtCore import QVariant
from qgis._core import (QgsProject, QgsLayerTree, QgsFieldConstraints)
from qgis._core import (QgsVectorLayer, QgsField, QgsMessageLog, QgsVectorFileWriter, QgsCoordinateTransformContext)

from model.m_layer import IMapLayer
from model.m_qgis import IQgis
from q_impl import MapLayer, PointsMapLayer
from srapp_model.model import m_project
from srapp_model.model.m_project import Project

FILED_TYPE_TO_QGS_FIELD_TYPE: dict[m_project.FieldType, int] = {
    m_project.FieldType.STRING: QVariant.String,
    m_project.FieldType.DOUBLE: QVariant.Double,
    m_project.FieldType.BOOL: QVariant.Bool,
    m_project.FieldType.INT: QVariant.Int,
    m_project.FieldType.DATETIME: QVariant.DateTime,
}

CONSTRAINTS = 'constraints'


class LayerFieldCreator(m_project.IFieldCreator):

    def make_field(self, constraints: QgsFieldConstraints = None, **kwargs) -> QgsField:
        field = QgsField(**kwargs)
        if constraints:
            field.setConstraints(constraints)
        return field

    def get_field_type(self, field_type: m_project.FieldType) -> int:
        return FILED_TYPE_TO_QGS_FIELD_TYPE.get(field_type)


def create_files(project: Project):
    Path(project.dir).mkdir(parents=True, exist_ok=True)
    _create_layers(project)


def _create_layers(project: Project):
    creator = LayerFieldCreator()
    _create_layer(project, 'Point', m_project.POINTS_LAYER_STR, m_project.points_fields(creator))
    _create_layer(project, 'None', m_project.BOREHOLES_LAYER_STR, m_project.boreholes_fields(creator))
    _create_layer(project, 'None', m_project.BOREHOLE_PERSONS_LAYER_STR, m_project.persons_fields(creator))
    _create_layer(project, 'None', m_project.LAYERS_LAYER_STR, m_project.layers_fields(creator))
    _create_layer(project, 'None', m_project.DRILLED_WATER_LAYER_STR, m_project.drilled_water_fields(creator))
    _create_layer(project, 'None', m_project.SET_WATER_LAYER_STR, m_project.set_water_fields(creator))
    _create_layer(project, 'None', m_project.EXUDATIONS_LAYER_STR, m_project.exudations_fields(creator))
    _create_layer(project, 'None', m_project.PROBES_LAYER_STR, m_project.probes_fields(creator))
    _create_layer(project, 'None', m_project.PROBE_UNITS_LAYER_STR, m_project.probe_unit_fields(creator))
    _create_layer(project, 'None', m_project.PROBE_PERSONS_LAYER_STR, m_project.persons_fields(creator))
    _create_layer(project, 'None', m_project.SHEARS_TODO_LAYER_STR, m_project.shears_todo_fields(creator))
    _create_layer(project, 'None', m_project.SHEAR_UNITS_LAYER_STR, m_project.shear_unit_fields(creator))
    _create_layer(project, 'Point', m_project.TEAMS_LAYER_STR, m_project.teams_fields(creator))


def _create_layer(project: Project, geometry: str, layer_name: str, fields: []):
    layer_options = QgsVectorLayer.LayerOptions()
    layer = QgsVectorLayer(geometry, layer_name, 'memory', layer_options)
    # if layer_name == m_project.POINTS_LAYER_STR:
    #     layer.setFieldConstraint(2, QgsFieldConstraints.Constraint.ConstraintNotNull)
    if not layer.isValid():
        QgsMessageLog.logMessage(f'Nieprawidłowa warstwa {layer_name}', 'SRApp')
        return
    pr = layer.dataProvider()
    pr.addAttributes(fields)
    layer.updateFields()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.fileEncoding = 'UTF-8'
    save_options.layerName = layer_name
    if not os.path.isfile(project.gpkg_file_path):
        save_options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
    else:
        save_options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer
    transform_context = QgsCoordinateTransformContext()
    writer = QgsVectorFileWriter.writeAsVectorFormatV3(layer, project.gpkg_file_path, transform_context, save_options)
    del writer


def add_project_to_qgis(project: Project):
    plugin_group_name = 'srapp'
    project_name = project.name
    qgs = QgsProject.instance()
    root = qgs.layerTreeRoot()
    plugin_group = root.findGroup(plugin_group_name)
    if not plugin_group:
        plugin_group = root.addGroup(plugin_group_name)
    project_group = root.findGroup(project_name)
    if not project_group:
        project_group = plugin_group.addGroup(project_name)

    def layer_supplier(layer_name: str):
        return _add_layer_to_qgis(project.gpkg_file_path, project_group, qgs, layer_name)

    set_project_layers(layer_supplier, project, IQgis(qgs))


def set_project_layers(layer_supplier: Callable[[str], Any], project: Project, iqgis: IQgis):
    map_layers: OrderedDict[str, IMapLayer] = OrderedDict()
    for layer_name in project.layers_names:
        qgis_layer = layer_supplier(layer_name)
        constructor: callable
        if layer_name == m_project.POINTS_LAYER_STR or layer_name == m_project.TEAMS_LAYER_STR:
            constructor = PointsMapLayer
        else:
            constructor = MapLayer
        layer = constructor(qgis_layer, iqgis)
        map_layers.update({layer_name: layer})
    project.set_layers(**map_layers)


LAYER_NAME_TO_FIELDS_CONSTRAINTS: Dict[str, Dict[int, Set[QgsFieldConstraints.Constraint]]] = {
    m_project.POINTS_LAYER_STR: {
        2: {QgsFieldConstraints.Constraint.ConstraintNotNull, QgsFieldConstraints.Constraint.ConstraintUnique}},
    m_project.BOREHOLES_LAYER_STR: {
        2: {QgsFieldConstraints.Constraint.ConstraintNotNull, QgsFieldConstraints.Constraint.ConstraintUnique}},
    m_project.PROBES_LAYER_STR: {
        2: {QgsFieldConstraints.Constraint.ConstraintNotNull, QgsFieldConstraints.Constraint.ConstraintUnique},
        8: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.TEAMS_LAYER_STR: {
        2: {QgsFieldConstraints.Constraint.ConstraintNotNull, QgsFieldConstraints.Constraint.ConstraintUnique}},
    m_project.SHEARS_TODO_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                      2: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.BOREHOLE_PERSONS_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                           2: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.PROBE_PERSONS_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                        2: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.LAYERS_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                 2: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.DRILLED_WATER_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                        2: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                        3: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.SET_WATER_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                    2: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                    3: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.EXUDATIONS_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                     2: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                     3: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.PROBE_UNITS_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                      2: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                      3: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
    m_project.SHEAR_UNITS_LAYER_STR: {1: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                      2: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                      3: {QgsFieldConstraints.Constraint.ConstraintNotNull},
                                      4: {QgsFieldConstraints.Constraint.ConstraintNotNull}},
}


def _add_layer_to_qgis(gpkg_file_path: str, group: QgsLayerTree, qgs: QgsProject, layer_name: str):
    layer_path = f'{gpkg_file_path}|layername={layer_name}'
    tmp_layer = QgsVectorLayer(layer_path, layer_name, 'ogr')
    layer: QgsVectorLayer = qgs.addMapLayer(tmp_layer, False)
    group.addLayer(layer)
    layer.setReadOnly(True)

    fields_idx_to_constraints = LAYER_NAME_TO_FIELDS_CONSTRAINTS.get(layer_name)
    for idx, constraints in fields_idx_to_constraints.items():
        for constraint in constraints:
            layer.setFieldConstraint(idx, constraint, QgsFieldConstraints.ConstraintStrength.ConstraintStrengthHard)

    QgsMessageLog.logMessage(f'Dodano warstwę "{layer_name}"', 'SRApp')
    return layer
