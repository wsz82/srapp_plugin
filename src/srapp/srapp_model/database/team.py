import dataclasses
from typing import *

from database import data
from database.data import Data, PointData

TEAM_ID_REMOTE = 'id'
X_REMOTE = 'x'
Y_REMOTE = 'y'


def team_local_names() -> List[str]:
    return [
        data.TIME,
        data.NAME,
    ]


@dataclasses.dataclass(frozen=True)
class TeamPoint(PointData):
    timestamp: str
    name: str

    @staticmethod
    def from_dict(doc_map: dict) -> 'TeamPoint':
        raw_remote_time = doc_map.get(data.TIME_REMOTE)
        time = Data.remote_time_to_local(raw_remote_time)
        return TeamPoint(
            float(doc_map.get(X_REMOTE)),
            float(doc_map.get(Y_REMOTE)),
            time,
            doc_map.get(TEAM_ID_REMOTE),
        )

    def attrs(self):
        return [
            self.timestamp,
            self.name,
        ]
