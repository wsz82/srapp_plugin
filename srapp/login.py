from . import auth
from .user import User
from .view.login import LoginForm

login_window = LoginForm()


def login() -> User:
    global login_window
    username, password = login_window.get_username_with_password()
    if username and password:
        firestore_client = auth.create_database_client(username, password)
        return User(username, firestore_client)
    else:
        raise LoginError(f'Invalid credentials for user: "{username}"')


class LoginError(ValueError):
    pass
