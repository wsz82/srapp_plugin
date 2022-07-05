from google.cloud import firestore_v1
from google.cloud.firestore_v1 import DocumentReference, CollectionReference

from database import constants

USERS_REMOTE = 'users'
VERSIONS_REMOTE = 'versions'
PROJECTS_REMOTE = 'projects'
BOREHOLES_REMOTE = 'boreholes'
PROBES_REMOTE = 'probes'
POINTS_REMOTE = 'map_points'
TEAMS_REMOTE = 'teams'
PROPERTIES_REMOTE = 'properties'
CRS_REMOTE = 'crs'


class User:
    def __init__(self, email: str, client: firestore_v1.Client):
        self.email: str = email
        self.client: firestore_v1.Client = client

    def is_auth(self):
        return self.client is not None

    def project_ref(self, project_name) -> DocumentReference:
        return self.client.collection(USERS_REMOTE).document(self.email).collection(VERSIONS_REMOTE) \
            .document(constants.DATABASE_VERSION).collection(PROJECTS_REMOTE).document(project_name)

    def map_points_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(POINTS_REMOTE)

    def boreholes_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(BOREHOLES_REMOTE)

    def probes_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(PROBES_REMOTE)

    def teams_ref(self, project_name) -> CollectionReference:
        return self.project_ref(project_name).collection(TEAMS_REMOTE)

    def crs_ref(self, project_name) -> DocumentReference:
        return self.project_ref(project_name).collection(PROPERTIES_REMOTE).document(CRS_REMOTE)
