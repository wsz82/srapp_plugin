import os
from typing import *

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QAction
from qgis._core import QgsProject
from qgis._gui import QgisInterface

import q_impl
# setup logger
from srapp_model.database import constants
from model.m_project import file_name_to_name
from srapp_model import G

G.Log = q_impl.Logger()

import q_auth as auth
from engine import synchronize
from engine.synchronize import Synchronizer
from model.m_qgis import IQgis
from model.m_user import User
from q_auth import LoginError
from q_impl import Qgis
from srapp import q_project
from srapp_model.model.m_project import Project

_sync_instance: Synchronizer = None
_user: User = None


def _try_login() -> User:
    global _user
    if _user and _user.is_auth():
        G.Log.message(f'Użytkownik "{_user.email}" zalogowany')
    else:
        try:
            _user = auth.login()
        except LoginError:
            _user = User('', None)
            G.Log.information('Odmowa dostępu')
        else:
            email = _user.email
            if _user.is_auth():
                G.Log.message(f'Udane logowanie użytkownika "{email}"')
            else:
                G.Log.message(f'Nieudane logowanie użytkownika "{email}"')
    return _user


class SrappPlugin:

    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.sync_action = None
        self.add_project_action = None

    def initGui(self):
        synchronize_icon = QIcon(self.make_icon_path('synchronize.png'))
        self.sync_action = QAction(synchronize_icon, 'Synchronizacja', self.iface.mainWindow())
        self.sync_action.setCheckable(True)
        self.sync_action.triggered.connect(self.run_sync)
        self.sync_action.changed.connect(self.resolve_push_actions_visibility)
        self.iface.addToolBarIcon(self.sync_action)

        project_icon = QIcon(self.make_icon_path('project.png'))
        self.add_project_action = QAction(project_icon, 'Temat', self.iface.mainWindow())
        self.add_project_action.triggered.connect(self.run_add_project)
        self.iface.addToolBarIcon(self.add_project_action)

    def make_icon_path(self, name):
        path = os.path.dirname(os.path.abspath(__file__))
        rel_path = 'resources\\icons'
        icon_path = os.path.join(path, rel_path, name)
        return icon_path

    def resolve_push_actions_visibility(self):
        is_sync = self.sync_action.isChecked()
        self.add_project_action.setDisabled(is_sync)

    def run_sync(self, is_pushed):
        global _sync_instance
        if is_pushed:
            user = _try_login()
            if user.is_auth():
                projects = self._scan_for_projects()
                _sync_instance = synchronize.Synchronizer(Qgis(self.iface), user, projects)
                _sync_instance.synchronize()
            else:
                G.Log.message(f'Nieudana synchronizacja')
                self.sync_action.setChecked(False)
        else:
            _sync_instance.desynchronize()

    def unload(self):
        self.iface.removeToolBarIcon(self.sync_action)
        del self.sync_action
        self.iface.removeToolBarIcon(self.add_project_action)

    def run_add_project(self):
        qid = QInputDialog()
        title = "Wpisz nazwę tematu"
        label = "Temat: "
        mode = QLineEdit.Normal
        default = constants.DEFAULT_PROJECT
        text, ok = QInputDialog.getText(qid, title, label, mode, default)
        if ok:
            project_name = text
            projects = self._scan_for_projects()
            project_names = [p.name for p in projects]
            if project_name in project_names:
                G.Log.information(f'Temat o nazwie "{project_name}" już istnieje')
                return
            self._create_project(project_name)

    def _create_project(self, project_name):
        G.Log.message(f'Tworzy temat "{project_name}"')

        projects_dir = self.make_projects_dir()
        new_project = Project(project_name, projects_dir)
        if os.path.isfile(new_project.gpkg_file_path):
            qm = QMessageBox
            ret = QMessageBox.question(None, 'Potwierdź', f'Plik .gpkg z podaną nazwą "{project_name}" już istnieje. '
                                                          f'Czy utworzyć nowy plik?', qm.Yes | qm.No)
            if ret == qm.No:
                G.Log.message(f'Przerwano tworzenie tematu "{project_name}"')
                q_project.add_project_to_qgis(new_project)
                return
        q_project.create_files(new_project)
        if os.path.isfile(new_project.gpkg_file_path):
            q_project.add_project_to_qgis(new_project)
        else:
            G.Log.information(f'Błąd tworzenia tematu "{new_project.gpkg_file_path}"')
            return
        G.Log.message(f'Utworzono temat "{project_name}"')

    def make_projects_dir(self) -> str:
        home_dir = os.path.expanduser('~')
        return os.path.join(home_dir, 'srapp', 'tematy')

    def _scan_for_projects(self) -> List[Project]:
        plugin_group_name = 'srapp'
        projects_dir = self.make_projects_dir()
        projects = []

        qgs = QgsProject.instance()
        root = qgs.layerTreeRoot()

        for file in os.listdir(projects_dir):
            if file.endswith('.gpkg'):
                name = os.path.splitext(file)[0]
                name = file_name_to_name(name)
                G.Log.message(f'Skanowanie tematów - wykryto plik: "{file}"')
                plugin_group = root.findGroup(plugin_group_name)
                if not plugin_group:
                    G.Log.message(f'Grupa "{plugin_group_name}" nie jest dodana do widoku warstw')
                    continue
                project_group = plugin_group.findGroup(name)
                if not project_group:
                    G.Log.message(f'Temat "{name}" nie jest dodany do widoku warstw')
                    continue
                project = Project(name, projects_dir)
                layers = project_group.findLayers()
                name_to_index = {l.name(): layers.index(l) for l in layers}

                def get_layer(layer_name: str):
                    return layers[name_to_index.get(layer_name)].layer()

                q_project.set_project_layers(get_layer, project, IQgis(qgs))

                projects.append(project)
        return projects
