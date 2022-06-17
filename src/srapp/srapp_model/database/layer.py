import dataclasses

from database import data
from model import LocalToRemote
from srapp_model.database.data import Data

TO = 'przelot'
TYPE = 'rodzaj'
ADMIXTURES = 'domiesz'
INTERBEDDINGS = 'przewar'
COLOR = 'kolor'
MOISTURE = 'wilgotn'
ROLLS_NUMBER = 'il_wal'
SOIL_STATE = 'st_gr'
SAMPLING = 'oprob'
DESCRIPTION = 'opis'

TO_REMOTE = 'to'
TYPE_REMOTE = 'type'
ADMIXTURES_REMOTE = 'admixtures'
INTERBEDDINGS_REMOTE = 'interbeddings'
COLOR_REMOTE = 'color'
MOISTURE_REMOTE = 'moisture'
ROLLS_NUMBER_REMOTE = 'rollsNumber'
SOIL_STATE_REMOTE = 'soilState'
SAMPLING_REMOTE = 'sampling'
DESCRIPTION_REMOTE = 'desc'

LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.NAME, data.NAME_REMOTE),
    (TO, TO_REMOTE),
    (TYPE, TYPE_REMOTE),
    (ADMIXTURES, ADMIXTURES_REMOTE),
    (INTERBEDDINGS, INTERBEDDINGS_REMOTE),
    (COLOR, COLOR_REMOTE),
    (MOISTURE, MOISTURE_REMOTE),
    (ROLLS_NUMBER, ROLLS_NUMBER_REMOTE),
    (SOIL_STATE, SOIL_STATE_REMOTE),
    (SAMPLING, SAMPLING_REMOTE),
    (DESCRIPTION, DESCRIPTION_REMOTE),
])


@dataclasses.dataclass(frozen=True)
class Layer(Data):
    name: str
    to: float
    type: str
    admixtures: str
    interbeddings: str
    color: str
    moisture: str
    rollsNumber: str
    soilState: str
    sampling: float
    desc: str

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return LOCAL_TO_REMOTE

    @staticmethod
    def from_dict(name: str, doc_map: {}) -> 'Layer':
        try:
            sampling = float(doc_map.get(SAMPLING_REMOTE, 0))
        except ValueError:
            sampling = None
        return Layer(
            name,
            float(doc_map.get(TO_REMOTE)),
            doc_map.get(TYPE_REMOTE, ''),
            doc_map.get(ADMIXTURES_REMOTE, ''),
            doc_map.get(INTERBEDDINGS_REMOTE, ''),
            doc_map.get(COLOR_REMOTE, ''),
            doc_map.get(MOISTURE_REMOTE, ''),
            doc_map.get(ROLLS_NUMBER_REMOTE, ''),
            doc_map.get(SOIL_STATE_REMOTE, ''),
            sampling,
            doc_map.get(DESCRIPTION_REMOTE, '')
        )

    def attrs(self):
        return [
            self.name,
            self.to,
            self.type,
            self.admixtures,
            self.interbeddings,
            self.color,
            self.moisture,
            self.rollsNumber,
            self.soilState,
            self.sampling,
            self.desc
        ]
