import os
import subprocess
import sys
import typing

try:
    import firebase_admin
except:
    py_path = sys.executable
    # Windows QGiS specific
    if 'qgis-bin.exe' in py_path:
        osgeo4w_path = os.path.dirname(os.path.dirname(py_path))
        py_path = os.path.join(osgeo4w_path, 'apps', 'Python39', 'python.exe')
    # install firebase_admin
    subprocess.check_call([py_path, "-m", "pip", "install", "firebase_admin"])

from PyQt5.QtWidgets import QAction, QMessageBox, QInputDialog, QLineEdit
from qgis._gui import QgisInterface
from qgis._core import QgsMessageLog, QgsProject
from qgis.PyQt.QtWidgets import QMessageBox, QAction
from . import project
from . import synchronize
from . import login
from . import push
from . import user
from .user import User

_sync_instance: synchronize.Synchronizer = None
_user: user.User = None


def _try_login() -> User:
    global _user
    if _user and _user.is_auth():
        QgsMessageLog.logMessage(f'Użytkownik "{_user.email}" zalogowany', 'SRApp')
    else:
        try:
            _user = login.login()
        except login.LoginError:
            _user = User('', None)
            QMessageBox.information(None, '', 'Nieudane logowanie')
        else:
            email = _user.email
            if _user.is_auth():
                QgsMessageLog.logMessage(f'Udane logowanie użytkownika "{email}"', 'SRApp')
            else:
                QgsMessageLog.logMessage(f'Nieudane logowanie użytkownika "{email}"', 'SRApp')
    return _user


class SrappPlugin:

    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        self.sync_action = QAction('Synchronizacja', self.iface.mainWindow())
        self.sync_action.setCheckable(True)
        self.sync_action.triggered.connect(self.run_sync)
        self.sync_action.changed.connect(self.resolve_push_actions_visibility)
        self.iface.addToolBarIcon(self.sync_action)

        self.add_project_action = QAction('Temat', self.iface.mainWindow())
        self.add_project_action.triggered.connect(self.run_add_project)
        self.iface.addToolBarIcon(self.add_project_action)

        self.add_action = QAction('Dodaj punkty', self.iface.mainWindow())
        self.add_action.triggered.connect(self._run_add)
        self.iface.addToolBarIcon(self.add_action)

        self.change_action = QAction('Zmień punkty', self.iface.mainWindow())
        self.change_action.triggered.connect(self._run_change)
        self.iface.addToolBarIcon(self.change_action)
        self.iface.addToolBarIcon(self.add_action)

        self.delete_action = QAction('Usuń punkty', self.iface.mainWindow())
        self.delete_action.triggered.connect(self._run_delete)
        self.iface.addToolBarIcon(self.delete_action)

    def resolve_push_actions_visibility(self):
        is_sync = self.sync_action.isChecked()
        self.add_project_action.setDisabled(is_sync)
        self.add_action.setDisabled(is_sync)
        self.change_action.setDisabled(is_sync)
        self.delete_action.setDisabled(is_sync)

    def run_sync(self, is_pushed):
        global _sync_instance
        if is_pushed:
            user = _try_login()
            if user.is_auth():
                projects = scan_for_projects()
                _sync_instance = synchronize.Synchronizer(user.email, user.client, projects)
                _sync_instance.synchronize()
            else:
                QgsMessageLog.logMessage(f'Nieudana synchronizacja', 'SRApp')
                self.sync_action.setChecked(False)
        else:
            _sync_instance.desynchronize()

    def unload(self):
        self.iface.removeToolBarIcon(self.sync_action)
        del self.sync_action
        self.iface.removeToolBarIcon(self.add_project_action)
        del self.add_project_action
        self.iface.removeToolBarIcon(self.add_action)
        del self.add_action
        self.iface.removeToolBarIcon(self.change_action)
        del self.change_action
        self.iface.removeToolBarIcon(self.delete_action)
        del self.delete_action

    def run_add_project(self):
        qid = QInputDialog()
        title = "Wpisz nazwę tematu"
        label = "Temat: "
        mode = QLineEdit.Normal
        default = "test"
        text, ok = QInputDialog.getText(qid, title, label, mode, default)
        if ok:
            project_name = text
            create_project(project_name)

    def _run_add(self):
        qm = QMessageBox
        ret = qm.question(None, '', 'Czy dodać zaznaczone punkty do bazy danych?', qm.Yes | qm.No)
        if ret == qm.Yes:
            project, user = _check_push()
            if project:
                push.add_selected_points(project, user.email, user.client)

    def _run_change(self):
        qm = QMessageBox
        ret = qm.question(None, '', 'Czy zmienić zaznaczone punkty w bazie danych?', qm.Yes | qm.No)
        if ret == qm.Yes:
            project, user = _check_push()
            if project:
                push.change_selected_points(project, user.email, user.client)

    def _run_delete(self):
        qm = QMessageBox
        ret = qm.question(None, '', 'Czy usunąć zaznaczone punkty w bazie danych?', qm.Yes | qm.No)
        if ret == qm.Yes:
            project, user = _check_push()
            if project:
                push.delete_selected_points(project, user.email, user.client, self.iface)


def _check_push() -> typing.Tuple[project.Project, user.User]:
    user = _try_login()
    if not user.is_auth():
        QMessageBox.information(None, 'Błąd', 'Brak zalogowanego użytkownika')
        return None, user
    projects = scan_for_projects()

    qgs = QgsProject.instance()
    root = qgs.layerTreeRoot()
    checked_layers = root.checkedLayers()
    points_layers = [layer for layer in checked_layers if layer.name() == project.POINTS_LAYER_STR]
    if points_layers:
        if len(points_layers) != 1:
            QMessageBox.information(None, 'Błąd',
                                    'Proszę zaznczyć tylko jedną warstwę "punkty" projektu, który ma być zaktualizowany')
        else:
            selected_project = projects[0]
            return selected_project, user
    else:
        QMessageBox.information(None, 'Błąd',
                                'Proszę zaznaczyć warstwę "punkty" projektu, który ma być zaktualizowany')
    return None, user


def create_project(project_name):
    QgsMessageLog.logMessage(f'Tworzy temat "{project_name}"', 'SRApp')

    projects_dir = make_projects_dir()
    new_project = project.Project(project_name, projects_dir)
    new_project.create_files()
    if os.path.isfile(new_project.gpkg_file_path):
        new_project.add_project_to_qgis()
    else:
        QMessageBox.information(None, 'Błąd', f'Brak tematu "{new_project.gpkg_file_path}"')
    QgsMessageLog.logMessage(f'Utworzono temat "{project_name}"', 'SRApp')


def make_projects_dir() -> str:
    home_dir = os.path.expanduser('~')
    return os.path.join(home_dir, 'SRApp', 'tematy')


def scan_for_projects() -> typing.List[project.Project]:
    projects_dir = make_projects_dir()
    projects = []

    qgs = QgsProject.instance()
    root = qgs.layerTreeRoot()

    for file in os.listdir(projects_dir):
        if file.endswith('.gpkg'):
            name = os.path.splitext(file)[0]
            QgsMessageLog.logMessage(f'Skanowanie tematów - wykryto plik: "{file}"', 'SRApp')
            project_group = root.findGroup(name)
            if project_group is None:
                QgsMessageLog.logMessage(f'Temat "{name}" nie jest dodany do widoku warstw', 'SRApp')
                continue
            found_project = project.Project(name, projects_dir)
            layers = project_group.findLayers()
            name_to_index = {l.name(): layers.index(l) for l in layers}

            def get_layer(layer_name: str):
                return layers[name_to_index.get(layer_name)].layer()

            for layer_str, set_function in found_project.layer_name_to_layer_set.items():
                layer = get_layer(layer_str)
                set_function(layer)

            projects.append(found_project)
    return projects
