import dataclasses

from database import data
from database.data import PERSON, REMOTE_PERSONS
from model import LocalToRemote
from srapp_model.database.data import Data

LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.NAME, data.NAME_REMOTE),
    (PERSON, REMOTE_PERSONS),
])


@dataclasses.dataclass(frozen=True)
class Person(Data):
    point_name: str
    person_name: str

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return LOCAL_TO_REMOTE

    def attrs(self):
        return [
            self.point_name,
            self.person_name,
        ]
