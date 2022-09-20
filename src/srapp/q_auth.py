import json

import requests
from google.cloud.firestore import Client
from google.oauth2.credentials import Credentials
from requests.exceptions import HTTPError

from model.m_user import User
from srapp.view.login import LoginForm

FIREBASE_REST_API = "https://identitytoolkit.googleapis.com/v1/accounts"
PUBLIC_API_KEY = "AIzaSyDi9tJ99bL3T0iSHecYqlpFgLXjKIn0Orw"
DATABASE_NAME = "metrykaapp-1580965863672"

login_window = LoginForm()


def login() -> User:
    global login_window
    username, password = login_window.get_username_with_password()
    if username and password:
        try:
            firestore_client = _create_database_client(username, password)
        except LoginError as e:
            raise LoginError(e)
        else:
            return User(username, firestore_client)
    else:
        return User(username, None)


def _create_database_client(username: str, password: str) -> Client:
    response = _sign_in_with_email_and_password(PUBLIC_API_KEY, username, password)
    creds = Credentials(response['idToken'], response['refreshToken'], enable_reauth_refresh=True)
    return Client(DATABASE_NAME, creds)


def _sign_in_with_email_and_password(api_key: str, email: str, password: str):
    request_url = "%s:signInWithPassword?key=%s" % (FIREBASE_REST_API, api_key)
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})

    req = requests.post(request_url, headers=headers, data=data)
    try:
        req.raise_for_status()
    except HTTPError as e:
        raise LoginError(e)

    return req.json()


class LoginError(ValueError):
    pass
