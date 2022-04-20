import dataclasses
from decimal import Decimal
from .data import Data


@dataclasses.dataclass(frozen=True)
class Layer(Data):
    name: str
    to: Decimal
    type: str
    admixtures: str
    interbeddings: str
    color: str
    moisture: str
    rollsNumber: str
    soilState: str
    sampling: str
    desc: str

    @staticmethod
    def from_dict(name: str, doc_map: {}) -> 'Layer':
        return Layer(
            name,
            doc_map.get('to'),
            doc_map.get('type'),
            doc_map.get('admixtures'),
            doc_map.get('interbeddings'),
            doc_map.get('color'),
            doc_map.get('moisture'),
            doc_map.get('rollsNumber'),
            doc_map.get('soilState'),
            doc_map.get('sampling'),
            doc_map.get('desc')
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
