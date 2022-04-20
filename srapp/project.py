import os
from pathlib import Path
from typing import Dict, Callable, List

from qgis.PyQt.QtCore import QVariant
from qgis._core import (QgsVectorLayer, QgsField, QgsProject,
                        QgsLayerTree,
                        QgsMessageLog, QgsVectorFileWriter, QgsCoordinateTransformContext)

from .database import point

POINTS_LAYER_STR = 'punkty'
SHEARS_TODO_LAYER_STR = 'sciecia_do_zrobienia'
BOREHOLES_LAYER_STR = 'wiercenia'
LAYERS_LAYER_STR = 'wiercenia_warstwy'
DRILLED_WATER_LAYER_STR = 'woda_nawiercona'
SET_WATER_LAYER_STR = 'woda_ustalona'
EXUDATIONS_LAYER_STR = 'wysieki'
PROBES_LAYER_STR = 'sondowania'
SHEARS_LAYER_STR = 'sciecia_wykonane'


class Project:
    def __init__(self, name: str, projects_dir: str):
        self._name: str = name
        self._dir: str = projects_dir
        self._gpkg_file_path: str = os.path.join(self.dir, f'{name}.gpkg')
        self.points_layer: QgsVectorLayer = None
        self.boreholes_layer: QgsVectorLayer = None
        self.layers_layer: QgsVectorLayer = None
        self.drilled_water_horizons_layer: QgsVectorLayer = None
        self.set_water_horizons_layer: QgsVectorLayer = None
        self.exudations_layer: QgsVectorLayer = None
        self.probes_layer: QgsVectorLayer = None
        self.shears_todo_layer: QgsVectorLayer = None
        self.shears_layer: QgsVectorLayer = None
        self._layer_name_to_layer_set: Dict[str, Callable[[QgsVectorLayer], None]] = {
            POINTS_LAYER_STR: self.set_points_layer,
            BOREHOLES_LAYER_STR: self.set_boreholes_layer,
            LAYERS_LAYER_STR: self.set_layers_layer,
            DRILLED_WATER_LAYER_STR: self.set_drilled_water_horizons_layer,
            SET_WATER_LAYER_STR: self.set_set_water_horizons_layer,
            EXUDATIONS_LAYER_STR: self.set_exudations_layer,
            PROBES_LAYER_STR: self.set_probes_layer,
            SHEARS_TODO_LAYER_STR: self.set_shears_todo_layer,
            SHEARS_LAYER_STR: self.set_shears_layer,
        }

    @property
    def name(self):
        return self._name

    @property
    def dir(self):
        return self._dir

    @property
    def gpkg_file_path(self):
        return self._gpkg_file_path

    @property
    def layer_name_to_layer_set(self):
        return self._layer_name_to_layer_set

    def set_points_layer(self, layer: QgsVectorLayer):
        self.points_layer = layer

    def set_boreholes_layer(self, layer: QgsVectorLayer):
        self.boreholes_layer = layer

    def set_layers_layer(self, layer: QgsVectorLayer):
        self.layers_layer = layer

    def set_drilled_water_horizons_layer(self, layer: QgsVectorLayer):
        self.drilled_water_horizons_layer = layer

    def set_set_water_horizons_layer(self, layer: QgsVectorLayer):
        self.set_water_horizons_layer = layer

    def set_exudations_layer(self, layer: QgsVectorLayer):
        self.exudations_layer = layer

    def set_probes_layer(self, layer: QgsVectorLayer):
        self.probes_layer = layer

    def set_shears_todo_layer(self, layer: QgsVectorLayer):
        self.shears_todo_layer = layer

    def set_shears_layer(self, layer: QgsVectorLayer):
        self.shears_layer = layer

    def create_files(self):
        Path(self._dir).mkdir(parents=True, exist_ok=True)
        # if not os.path.isfile(self._gpkg_file_path):
        #     _create_layers(self)
        _create_layers(self)

    def add_project_to_qgis(self):
        name = self.name
        qgs = QgsProject.instance()
        root = qgs.layerTreeRoot()
        group = root.addGroup(name)

        for key, set_function in self.layer_name_to_layer_set.items():
            layer = self.add_layer_to_qgis(group, qgs, key)
            set_function(layer)

    def add_layer_to_qgis(self, group: QgsLayerTree, qgs: QgsProject, layer_name: str):
        layer_path = f'{self.gpkg_file_path}|layername={layer_name}'
        tmp_layer = QgsVectorLayer(layer_path, layer_name, 'ogr')
        layer = qgs.addMapLayer(tmp_layer, False)
        group.addLayer(layer)
        QgsMessageLog.logMessage(f'Dodano warstwę "{layer_name}"', 'SRApp')
        return layer

    def _delete_layer_features(self, layer: QgsVectorLayer):
        provider = layer.dataProvider()
        list_of_ids = [feat.id() for feat in provider.getFeatures()]
        provider.deleteFeatures(list_of_ids)

    def reset(self):
        self._delete_layer_features(self.points_layer)
        self._delete_layer_features(self.boreholes_layer)
        self._delete_layer_features(self.layers_layer)
        self._delete_layer_features(self.drilled_water_horizons_layer)
        self._delete_layer_features(self.set_water_horizons_layer)
        self._delete_layer_features(self.exudations_layer)
        self._delete_layer_features(self.probes_layer)
        self._delete_layer_features(self.shears_todo_layer)
        self._delete_layer_features(self.shears_layer)


def _create_layers(project: Project):
    _create_layer(project, 'Point', POINTS_LAYER_STR, _points_fields())
    _create_layer(project, 'None', BOREHOLES_LAYER_STR, _boreholes_fields())
    _create_layer(project, 'None', LAYERS_LAYER_STR, _layers_fields())
    _create_layer(project, 'None', DRILLED_WATER_LAYER_STR, _drilled_water_fields())
    _create_layer(project, 'None', SET_WATER_LAYER_STR, _set_water_horizons_fields())
    _create_layer(project, 'None', EXUDATIONS_LAYER_STR, _exudations_fields())
    _create_layer(project, 'None', PROBES_LAYER_STR, _probes_fields())
    _create_layer(project, 'None', SHEARS_TODO_LAYER_STR, _shears_todo_fields())
    _create_layer(project, 'None', SHEARS_LAYER_STR, _probe_shears_fields())


def _points_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name=point.NAME, comment='Nazwa', type=QVariant.String))
    fields.append(QgsField(name=point.CREATOR, comment='Twórca', type=QVariant.String))
    fields.append(QgsField(name=point.HEIGHT, comment='Wysokość', type=QVariant.Double, prec=2))
    fields.append(QgsField(name=point.HEIGHT_SYS, comment='Układ wysokości', type=QVariant.String))
    fields.append(QgsField(name=point.BOREHOLE_STATE, comment='Stan wiercenia', type=QVariant.String))
    fields.append(QgsField(name=point.PROBE_STATE, comment='Stan sondowania', type=QVariant.String))
    fields.append(
        QgsField(name=point.BOREHOLE_DEPTH, comment='Projektowana gł. wiercenia', type=QVariant.Double, prec=2))
    fields.append(QgsField(name=point.PROBE_DEPTH, comment='Projektowana gł. sondowania', type=QVariant.Double, prec=2))
    fields.append(QgsField(name=point.IS_STAKEOUT, comment='Czy wytyczone', type=QVariant.Bool))
    fields.append(QgsField(name=point.PROBE_TYPE, comment='Typ sondowania', type=QVariant.String))
    fields.append(QgsField(name=point.OWNER, comment='Właściciel', type=QVariant.String))
    fields.append(QgsField(name=point.CONTACT, comment='Kontakt', type=QVariant.String))
    fields.append(QgsField(name=point.ASSIGNED_PERFORMER, comment='Przypisany wykonawca', type=QVariant.String))
    fields.append(QgsField(name=point.COMMENT, comment='Komentarz', type=QVariant.String))
    return fields


def _shears_todo_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='gl_sciec', comment='Głębokość ścięcia', type=QVariant.Double, prec=2))
    return fields


def _boreholes_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='ost_wykon', comment='Ostatni wykonwaca', type=QVariant.String))
    fields.append(QgsField(name='wykonawcy', comment='Wykonawcy', type=QVariant.String))
    fields.append(QgsField(name='lokacja', comment='Lokacja', type=QVariant.String))
    fields.append(QgsField(name='nr_poj', comment='Nr. rejestracyjny pojazdu', type=QVariant.String))
    fields.append(QgsField(name='gl_pocz', comment='Głębokość początkowa', type=QVariant.Double, prec=2))
    fields.append(QgsField(name='typ', comment='Typ wiercenia', type=QVariant.String))
    return fields


def _layers_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='przelot', comment='Przelot', type=QVariant.Double, prec=2))
    fields.append(QgsField(name='rodzaj', comment='Rodzaj gruntu', type=QVariant.String))
    fields.append(QgsField(name='domiesz', comment='Domieszki gruntu', type=QVariant.String))
    fields.append(QgsField(name='przewar', comment='Przewarstwienia gruntu', type=QVariant.String))
    fields.append(QgsField(name='kolor', comment='Kolor gruntu', type=QVariant.String))
    fields.append(QgsField(name='wilgotn', comment='Wilgotność gruntu', type=QVariant.String))
    fields.append(QgsField(name='il_wal', comment='Ilość wałeczkowań', type=QVariant.String))
    fields.append(QgsField(name='st_gr', comment='Stan gruntu', type=QVariant.String))
    fields.append(QgsField(name='oprob', comment='Opróbowanie', type=QVariant.Double, prec=2))
    fields.append(QgsField(name='opis', comment='Opis gruntu', type=QVariant.String))
    return fields


def _drilled_water_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='warstwa', comment='Warstwa wodonośna', type=QVariant.String))
    fields.append(QgsField(name='gl_zwier', comment='Głębokość zwierciadłą', type=QVariant.Double))
    return fields


def _set_water_horizons_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='warstwa', comment='Warstwa wodonośna', type=QVariant.String))
    fields.append(QgsField(name='gl_zwier', comment='Głębokość zwierciadłą', type=QVariant.Double))
    fields.append(QgsField(name='czas_dni', comment='Czas pomairu po odwiercie - dni', type=QVariant.Int))
    fields.append(QgsField(name='czas_godz', comment='Czas pomairu po odwiercie - godziny', type=QVariant.Int))
    fields.append(QgsField(name='czas_min', comment='Czas pomairu po odwiercie - minuty', type=QVariant.Int))
    return fields


def _exudations_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='rodz_sacz', comment='Rodzaj sączenia', type=QVariant.String))
    fields.append(QgsField(name='glebok', comment='Głębokość', type=QVariant.Double))
    return fields


def _probes_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='ost_wykon', comment='Ostatni wykonwaca', type=QVariant.String))
    fields.append(QgsField(name='wykonawcy', comment='Wykonawcy', type=QVariant.String))
    fields.append(QgsField(name='lokacja', comment='Lokacja', type=QVariant.String))
    fields.append(QgsField(name='nr_poj', comment='Nr. rejestracyjny pojazdu', type=QVariant.String))
    fields.append(QgsField(name='gl_pocz', comment='Głębokość początkowa', type=QVariant.Double, prec=2))
    fields.append(QgsField(name='typ', comment='Typ sondowania', type=QVariant.String))
    fields.append(QgsField(name='interwal', comment='Interwał', type=QVariant.Double))
    fields.append(QgsField(name='jednostki', comment='Kolejne jednostki', type=QVariant.StringList))
    return fields


def _probe_shears_fields() -> List[QgsField]:
    fields = []
    fields.append(QgsField(name='punkt', comment='Punkt', type=QVariant.String))
    fields.append(QgsField(name='gl_sciec', comment='Głebokość ścięcia', type=QVariant.String))
    fields.append(QgsField(name='wartosci', comment='Wartości ścięcia', type=QVariant.String))
    return fields


def _create_layer(project: Project, geometry: str, base_name: str, fields: []):
    layer_options = QgsVectorLayer.LayerOptions()
    layer = QgsVectorLayer(geometry, base_name, 'memory', layer_options)
    if not layer.isValid():
        QgsMessageLog.logMessage(f'Nieprawidłowa warstwa {base_name}', 'SRApp')
        return
    pr = layer.dataProvider()
    pr.addAttributes(fields)
    layer.updateFields()
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.fileEncoding = 'UTF-8'
    save_options.layerName = base_name
    if not os.path.isfile(project.gpkg_file_path):
        save_options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteFile
    else:
        save_options.actionOnExistingFile = QgsVectorFileWriter.ActionOnExistingFile.CreateOrOverwriteLayer
    transform_context = QgsCoordinateTransformContext()
    writer = QgsVectorFileWriter.writeAsVectorFormatV3(layer, project.gpkg_file_path, transform_context, save_options)
    del writer
