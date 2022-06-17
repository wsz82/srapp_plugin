from google.cloud import firestore_v1
from google.cloud.firestore_v1 import DocumentReference, CollectionReference

from database import data


class User:
    def __init__(self, email: str, client: firestore_v1.Client):
        self.email: str = email
        self.client: firestore_v1.Client = client

    def is_auth(self):
        return self.client is not None

    def project_ref(self, project_name) -> DocumentReference:
        return self.client.collection(data.USERS_REMOTE).document(self.email).collection(data.PROJECTS_REMOTE).document(
            project_name)

    def map_points_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(data.POINTS_REMOTE)

    def boreholes_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(data.BOREHOLES_REMOTE)

    def probes_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(data.PROBES_REMOTE)

    def teams_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(data.TEAMS_REMOTE)
