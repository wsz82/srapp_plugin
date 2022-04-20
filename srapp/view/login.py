import typing

from PyQt5.QtWidgets import (QVBoxLayout, QDialogButtonBox, QDialog)
from qgis._core import QgsApplication, QgsAuthMethodConfig
from qgis._gui import QgsAuthConfigSelect


class LoginForm(QDialog):
    def __init__(self):
        super().__init__()
        self.auth_result: typing.Tuple[str, str]

        self.setWindowTitle('Zaloguj się')

        layout = QVBoxLayout()
        self.auth_selection = QgsAuthConfigSelect()
        layout.addWidget(self.auth_selection)

        buttons = QDialogButtonBox()
        buttons.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        layout.addWidget(buttons)

        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self._reject)

        self.setLayout(layout)

    def _accept(self):
        auth_manager = QgsApplication.authManager()
        config_id = self.auth_selection.configId()
        auth_config = QgsAuthMethodConfig()
        auth_manager.loadAuthenticationConfig(config_id, auth_config, True)
        username = auth_config.config('username')
        password = auth_config.config('password')
        self.auth_result = username, password
        self.close()

    def _reject(self):
        self.auth_result = '', ''
        self.close()

    def get_username_with_password(self) -> typing.Tuple[str, str]:
        self.exec()
        return self.auth_result
