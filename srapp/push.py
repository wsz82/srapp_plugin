from PyQt5.QtWidgets import QMessageBox
from google.cloud.firestore_v1 import Client, DocumentReference, CollectionReference
from qgis._core import QgsFeatureRequest, QgsExpression, QgsMessageLog
from qgis._gui import QgisInterface

from .database import point
from .database.point import Point
from .database.shear import TodoShear
from .project import Project


def _map_points_doc_ref(client, email, project) -> CollectionReference:
    project_ref: DocumentReference = client.collection('users').document(email).collection('projects').document(
        project.name)
    return project_ref.collection('map_points')


def _add_point(map_points_ref: CollectionReference, p: Point):
    point_map = p.__dict__
    point_number = p.pointNumber
    map_points_ref.add(point_map, point_number)
    QgsMessageLog.logMessage(f'Dodano punkt "{point_number}"', 'SRApp - baza danych')


def _change_point(map_points_ref: CollectionReference, p: Point):
    point_map = p.__dict__
    point_number = p.pointNumber
    map_points_ref.document(point_number).set(point_map)
    QgsMessageLog.logMessage(f'Zmieniono punkt "{point_number}"', 'SRApp - baza danych')


def add_selected_points(project: Project, email: str, client: Client):
    points = _get_points(project)
    map_points_ref = _map_points_doc_ref(client, email, project)
    for p in points:
        _add_point(map_points_ref, p)


def change_selected_points(project: Project, email: str, client: Client):
    points = _get_points(project)
    map_points_ref = _map_points_doc_ref(client, email, project)
    for p in points:
        _change_point(map_points_ref, p)


def delete_selected_points(project: Project, email: str, client: Client, iface: QgisInterface):
    points_layer = project.points_layer
    features = points_layer.selectedFeatures()
    if not features:
        QMessageBox.information(None, 'Błąd', 'Proszę zaznaczyć punkty, które mają być zaktualizowane')
        return
    map_points_ref = _map_points_doc_ref(client, email, project)
    for feat in features:
        name = feat.attributeMap().get(point.NAME)
        map_points_ref.document(name).delete()
        QgsMessageLog.logMessage(f'Usunięto punkt "{name}"', 'SRApp - baza danych')
    provider = points_layer.dataProvider()
    provider.deleteFeatures([feat.id() for feat in features])
    refresh_layer(iface, points_layer)


def refresh_layer(iface, layer):
    if iface.mapCanvas().isCachingEnabled():
        layer.triggerRepaint()
    else:
        iface.mapCanvas().refresh()


def _get_points(project):
    points_layer = project.points_layer
    shears_todo_layer = project.shears_todo_layer
    features = points_layer.selectedFeatures()
    points = []
    if not features:
        QMessageBox.information(None, 'Błąd', 'Proszę zaznaczyć punkty, które mają być zaktualizowane')
    for feat in features:
        name = feat.attributeMap().get(point.NAME)
        expression = QgsExpression(f'"{point.NAME}"=\'{name}\'')
        shears_todo_features = list(shears_todo_layer.getFeatures(QgsFeatureRequest(expression)))
        shears_todo = [TodoShear.from_feature(feat) for feat in shears_todo_features]
        p = Point.from_feature(feat, shears_todo)
        points.append(p)
    return points
