import datetime
from typing import *

from google.cloud.firestore_v1 import CollectionReference, DocumentReference
from google.cloud.firestore_v1.types import WriteResult

from database import data
from model.m_layer import IMapLayer
from srapp_model import G


def on_items_deleted(collection_ref: CollectionReference, names: Set[str]):
    for name in names:
        collection_ref.document(make_valid_id(name)).delete()
        G.Log.message(f'Usunięto "{name}"', 'SRApp - baza danych')


def on_items_modify(project_ref: DocumentReference, names: Set[str], layer: IMapLayer):
    items_ref: CollectionReference = project_ref.collection(layer.database_ref_path)
    for name in names:
        features = layer.features_by_name(name)
        all_items_map: dict = layer.features_to_remote(features)
        for item_name, item_map in all_items_map.items():
            time: str = item_map.pop(data.TIME_REMOTE)
            if time:
                item_map.update({data.TIME_REMOTE: _parse_time(time)})
            item_ref = items_ref.document(make_valid_id(item_name))
            item_ref.set(item_map, True)
            # todo check if success
            G.Log.message(f'Dodano "{item_name}"', 'SRApp - baza danych')


def _parse_time(time_str: str):
    return datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')


def on_subitems_modify(project_ref: DocumentReference, names: Set[str], layer: IMapLayer):
    items_ref: CollectionReference = project_ref.collection(layer.database_ref_path)
    for name in names:
        item_ref: DocumentReference = items_ref.document(make_valid_id(name))
        features = layer.features_by_name(name)
        assert features
        data_map = layer.features_to_remote(features)
        result: WriteResult = item_ref.set(data_map, True)
        # todo check if success
        G.Log.message(f'Zmodyfikowano "{name}"', 'SRApp - baza danych')


def make_valid_id(id: str) -> str:
    return id.replace('/', '**')
