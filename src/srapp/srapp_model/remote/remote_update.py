import datetime
from typing import *

from google.cloud.firestore_v1 import CollectionReference, DocumentReference
from google.cloud.firestore_v1.types import WriteResult

from model.m_layer import IMapLayer
from model.m_user import make_valid_id
from srapp_model import G

DATABASE_TAG = 'SRApp - baza danych'


def on_items_deleted(collection_ref: CollectionReference, names: Set[str], layer_name: str):
    for name in names:
        result = collection_ref.document(make_valid_id(name)).delete()
        G.Log.message(f'{layer_name}: usunięto "{name}"', DATABASE_TAG)


def on_items_modify(project_ref: DocumentReference, names: Set[str], layer: IMapLayer):
    items_ref: CollectionReference = project_ref.collection(layer.database_ref_path)
    for name in names:
        features = layer.features_by_name(name)
        all_items_map: dict = layer.features_to_remote(features)
        for item_name, item_map in all_items_map.items():
            item_ref = items_ref.document(make_valid_id(item_name))
            result: WriteResult = item_ref.set(item_map, True)
            result_message = make_result_message(result)
            G.Log.message(f'{layer.name}: zmieniono "{item_name}" - {result_message}', DATABASE_TAG)


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
        result_message = make_result_message(result)
        G.Log.message(f'{layer.name}: zmieniono "{name}" - {result_message}', DATABASE_TAG)


def make_result_message(result):
    if result.update_time:
        return 'powodzenie'
    else:
        return 'niepowodzenie'
