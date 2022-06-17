import dataclasses
from typing import *

from database import data
from model import LocalToRemote
from srapp_model.database.data import Data

SHEAR_DEPTH = 'gl_sciec'
SHEAR_DEPTH_REMOTE = 'depth'
INDEX = 'indeks'
VALUE = 'wartosc'
TORQUES_REMOTE = 'torques'
SHEARS_REMOTE = 'shears'


def shear_unit_local_names() -> List[str]:
    return [
        data.NAME,
        SHEAR_DEPTH,
        INDEX,
        VALUE,
    ]


@dataclasses.dataclass(frozen=True)
class ShearUnit(Data):
    name: str
    depth: float
    index: int
    torque: str

    def attrs(self) -> []:
        return [
            self.name,
            self.depth,
            self.index,
            self.torque,
        ]


SHEAR_TODO_LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.NAME, data.NAME_REMOTE),
    (SHEAR_DEPTH, SHEAR_DEPTH_REMOTE),
])


@dataclasses.dataclass(frozen=True)
class TodoShear(Data):
    name: str
    depth: float

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return SHEAR_TODO_LOCAL_TO_REMOTE

    def attrs(self) -> []:
        return [
            self.name,
            self.depth
        ]
