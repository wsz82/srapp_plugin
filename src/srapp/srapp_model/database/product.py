import dataclasses
from abc import ABC
from typing import Tuple

from database import data
from database.product_point import LAST_PERFORMER_REMOTE
from srapp_model.database.data import Data


@dataclasses.dataclass(frozen=True)
class Product(Data, ABC):
    timestamp: str
    name: str
    last_performer: str

    def attrs(self) -> []:
        return [
            self.timestamp,
            self.name,
            self.last_performer
        ]

    @staticmethod
    def product_from_dict(doc_map: {}) -> Tuple[str, str, str]:
        timestamp = Data.remote_time_to_local(doc_map.get(data.TIME_REMOTE, ''))
        name = doc_map.get(data.NAME_REMOTE)
        last_performer = doc_map.get(LAST_PERFORMER_REMOTE, '')
        return timestamp, name, last_performer
