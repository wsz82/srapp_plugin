import json
import requests

from requests.exceptions import HTTPError
from google.oauth2.credentials import Credentials
from google.cloud.firestore import Client

FIREBASE_REST_API = "https://identitytoolkit.googleapis.com/v1/accounts"
PUBLIC_API_KEY = "AIzaSyDi9tJ99bL3T0iSHecYqlpFgLXjKIn0Orw"
DATABASE_NAME = "metrykaapp-1580965863672"


def create_database_client(username: str, password: str) -> Client:
    response = _sign_in_with_email_and_password(PUBLIC_API_KEY, username, password)
    creds = Credentials(response['idToken'], response['refreshToken'])
    return Client(DATABASE_NAME, creds)


def _sign_in_with_email_and_password(api_key: str, email: str, password: str):
    request_url = "%s:signInWithPassword?key=%s" % (FIREBASE_REST_API, api_key)
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})

    req = requests.post(request_url, headers=headers, data=data)
    try:
        req.raise_for_status()
    except HTTPError as e:
        raise HTTPError(e)

    return req.json()


