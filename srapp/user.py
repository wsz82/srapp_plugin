from google.cloud import firestore_v1


class User:
    def __init__(self, email: str, client: firestore_v1.Client):
        self.email: str = email
        self.client: firestore_v1.Client = client

    def is_auth(self):
        return self.client is not None
