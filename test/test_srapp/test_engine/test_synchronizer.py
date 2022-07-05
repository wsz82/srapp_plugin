import datetime
from typing import *

import pytest
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from google.cloud.firestore_v1.watch import ChangeType

import logger
import model.m_config
from database.shear import TodoShear
from model.m_layer import IMapLayer
from srapp_model import G
from srapp_model import database
from srapp_model.database import data
from srapp_model.database import point, data
from srapp_model.database.data import FTR
from srapp_model.database.data import IFeature, Data
from srapp_model.database.point import Point
from srapp_model.engine.synchronize import Synchronizer
from srapp_model.logger import ILogger
from srapp_model.model.m_project import Project
from srapp_model.model.m_qgis import IQgis
from srapp_model.model.m_user import User
from test_srapp.fakes import FakeFeature, FakePointFeature


class FakeLogger(ILogger):
    def message(self, message: str, tag: str = logger.DEFAULT_MESSAGE_TAG):
        print(f'{tag}: {message}')

    def error(self, message: str, tag: str = logger.DEFAULT_ERROR_TAG):
        print(f'{tag}: {message}')

    def information(self, message: str, title: str = logger.DEFAULT_INFO_TITLE):
        print(f'{title}: {message}')


G.Log = FakeLogger()


class FakeQgis(IQgis[None]):

    def try_refresh(self) -> bool:
        return True


class FakeWatch:
    def unsubscribe(self):
        pass


class FakeProbesReference:
    def on_snapshot(self, func: callable):
        doc_snapshot = None
        changes = []
        read_time = None
        func(doc_snapshot, changes, read_time)
        return FakeWatch()


class FakeBoreholesReference:
    def on_snapshot(self, func: callable):
        doc_snapshot = None
        changes = []
        read_time = None
        func(doc_snapshot, changes, read_time)
        return FakeWatch()


class FakeMapPointsReference:
    def on_snapshot(self, on_update: callable) -> FakeWatch:
        FakeMapPointsReference.on_update = on_update
        doc_snapshot = None
        changes = []
        read_time = None
        FakeMapPointsReference.on_update(doc_snapshot, changes, read_time)
        return FakeWatch()

    @staticmethod
    def send_update(doc_snapshot, changes, read_time):
        FakeMapPointsReference.on_update(doc_snapshot, changes, read_time)


class FakeTeamsReference:
    def on_snapshot(self, on_update: callable) -> FakeWatch:
        FakeTeamsReference.on_update = on_update
        doc_snapshot = None
        changes = []
        read_time = None
        FakeTeamsReference.on_update(doc_snapshot, changes, read_time)
        return FakeWatch()

    @staticmethod
    def send_update(doc_snapshot, changes, read_time):
        FakeTeamsReference.on_update(doc_snapshot, changes, read_time)


class FakeCrsReference:
    def set(self, *args, **kwargs):
        pass


class FakeUser(User):

    def __init__(self, email: str):
        super().__init__(email, None)

    def is_auth(self):
        return True

    def map_points_ref(self, project_name) -> FakeMapPointsReference:
        return FakeMapPointsReference()

    def boreholes_ref(self, project_name) -> FakeBoreholesReference:
        return FakeBoreholesReference()

    def probes_ref(self, project_name) -> FakeProbesReference:
        return FakeProbesReference()

    def teams_ref(self, project_name) -> FakeTeamsReference:
        return FakeTeamsReference()

    def crs_ref(self, project_name) -> FakeCrsReference:
        return FakeCrsReference()


class FakeConnectable:
    def connect(self, func: callable):
        pass

    def disconnect(self, func: callable):
        pass


FKFTR = TypeVar('FTR', FakeFeature, FakePointFeature)


class FakeMapLayer(IMapLayer, Generic[FKFTR]):

    def __init__(self, id: str, features: List[FKFTR], qgis: IQgis):
        super().__init__(None, qgis)
        self._id = id
        self._features = features or []

    def _committed_features_added_func(self) -> callable:
        return FakeConnectable()

    def _committed_features_removed_func(self) -> callable:
        return FakeConnectable()

    def _committed_attribute_values_changes_func(self) -> callable:
        return FakeConnectable()

    def wrap_raw_feature(self, feature: FTR) -> IFeature:
        pass

    def make_timestamp_field(self, timestamp: datetime.datetime):
        return timestamp

    def _add_feature(self, item: Data):
        fids = [f.fid() for f in self._features]
        max_fid = max(fids) if fids else 0
        fid = max_fid + 1
        values = item.attrs()
        keys = item.fields_names()
        kwargs = dict(zip(keys, values))

        self._features.append(self._make_fake_feature(fid, item, **kwargs))
        # inform listeners

    def _make_fake_feature(self, fid: int, item: Data, **kwargs) -> FKFTR:
        return FakeFeature(item.fields_names(), fid, **kwargs)

    def _delete_features(self, id: int):
        def fil(f: FKFTR):
            return f.fid() == id

        to_del = filter(fil, self._features)
        for f in to_del:
            self._features.remove(f)

    def id(self):
        return self._id

    def refresh(self):
        pass

    def features_by_name(self, name: str) -> List[IFeature]:
        return [f for f in self._features if f.name() == name]

    def all_features(self) -> List[IFeature]:
        return self._features

    def change_attribute_values(self, attr_map: Dict[int, Dict[int, Any]]):
        for f in self._features:
            fid = f.fid()
            if fid in attr_map.keys():
                f_map = attr_map.get(fid)
                f.set_attributes(list(f_map.values()))

    def delete_all_features(self):
        self._features.clear()

    def delete_features_by_name(self, name: str):
        [self._features.remove(f) for f in self._features if f.name() == name]


class FakePointsMapLayer(FakeMapLayer, IMapLayer):

    def _make_fake_feature(self, fid: int, item: Point, **kwargs) -> FKFTR:
        return FakePointFeature(point.LOCAL_TO_REMOTE.local_names(), fid, item.x, item.y, **kwargs)


class FakeDocument:
    def __init__(self, doc_map: dict):
        self.doc_map = doc_map
        self.id = doc_map.get(database.data.NAME_REMOTE)

    def to_dict(self):
        return self.doc_map


class FakeChange:
    def __init__(self, change_type: ChangeType, document: FakeDocument):
        self.type = change_type
        self.document = document


class TestSynchronizer:

    @pytest.fixture
    def point_D1(self) -> dict:
        return {'x': 460797.19,
                'boreholeStatus': 'EMPTY',
                'heightSystem': 'PL-KRON86-NH',
                'assignedPerformer': 'wnijtek',
                'height': 86.7,
                'owner': '',
                'pointNumber': 'D1',
                'probeDesignedDepth': '0.0',
                'timestamp': DatetimeWithNanoseconds(2022, 5, 31, 6, 17, 1, tzinfo=datetime.timezone.utc),
                'comments': None,
                'probeStatus': 'EMPTY',
                'creator': 'wojtek',
                'isStakeoutDone': False,
                'contact': '',
                'y': 488728.8,
                'shearsToDoList': [5.1],
                'probeType': '',
                'boreholeDesignedDepth': '0.0'}

    @pytest.fixture
    def point_D4(self) -> dict:
        return {'x': 460797.19,
                'boreholeStatus': 'EMPTY',
                'heightSystem': 'PL-KRON86-NH',
                'assignedPerformer': 'wnijtek',
                'height': 86.7,
                'owner': '',
                'pointNumber': 'D4',
                'probeDesignedDepth': '0.0',
                'timestamp': DatetimeWithNanoseconds(2022, 5, 3, 6, 17, 1, tzinfo=datetime.timezone.utc),
                'comments': None,
                'probeStatus': 'EMPTY',
                'creator': 'wojtek',
                'isStakeoutDone': False,
                'contact': '',
                'y': 488728.8,
                'shearsToDoList': [2.5, 3.3],
                'probeType': '',
                'boreholeDesignedDepth': '0.0'}

    def send_point(self, point: dict):
        FakeMapPointsReference.send_update(None, [FakeChange(ChangeType.ADDED, FakeDocument(point))], None)

    def remove_point(self, point: dict):
        FakeMapPointsReference.send_update(None, [FakeChange(ChangeType.REMOVED, FakeDocument(point))], None)

    @pytest.fixture
    def sync_instance(self) -> Synchronizer:
        qgis = FakeQgis(None)
        project = Project('test', '/fake/dir')
        shears = [TodoShear('D1', 1.5), TodoShear('D1', 1.9)]
        points = [
            Point(0, 0, OrderedDict([(data.TIME, datetime.datetime.now()), (data.NAME, 'D1')]), shears),
            Point(0, 0, OrderedDict([(data.TIME, datetime.datetime.now()), (data.NAME, 'D2')]), []),
            Point(0, 0, OrderedDict([(data.TIME, datetime.datetime.now()), (data.NAME, 'D3')]), []),
        ]
        project.points_layer = FakePointsMapLayer(model.m_config.POINTS_LAYER_STR, [], qgis)
        for p in points:
            point_name: str = p.attrs()[1]
            project.points_layer.add_feature(p, point_name)
        project.shears_todo_layer = FakeMapLayer(model.m_config.SHEARS_TODO_LAYER_STR, [], qgis)
        project.shears_todo_layer.add_features(shears, 'D1')
        projects = [project]
        synchronizer = Synchronizer(qgis, FakeUser('fake@mail.com'), projects)
        synchronizer.synchronize()
        return synchronizer

    def test_listeners_stop(self, sync_instance):
        assert len(sync_instance._listeners) != 0
        sync_instance.desynchronize()
        assert len(sync_instance._listeners) == 0

    def test_point_is_deleted(self, sync_instance, point_D1):
        self.remove_point(point_D1)
        features = sync_instance.projects[0].points_layer.all_features()
        assert len(features) == 2

    def test_last_fid_to_id_is_updated(self, sync_instance, point_D4):
        fids_to_names = sync_instance.projects[0].points_layer.fid_to_name
        assert fids_to_names.get(1) == 'D1'
        assert fids_to_names.get(2) == 'D2'
        assert fids_to_names.get(3) == 'D3'
        self.send_point(point_D4)
        assert fids_to_names.get(4) == 'D4'

    def test_shears_todo_are_populated(self, sync_instance):
        layer = sync_instance.projects[0].shears_todo_layer
        features = layer.features_by_name('D1')
        assert len(features) == 2

    def test_shears_todo_are_updated(self, sync_instance, point_D4):
        self.send_point(point_D4)
        layer = sync_instance.projects[0].shears_todo_layer
        features = layer.all_features()
        assert len(features) == 4

    def test_shears_todo_of_the_same_point_are_updated(self, sync_instance, point_D1):
        self.send_point(point_D1)
        layer = sync_instance.projects[0].shears_todo_layer
        features = layer.features_by_name('D1')
        assert len(features) == 1

    def test_shears_todo_are_removed(self, sync_instance, point_D1):
        point_D1.update({'shearsToDoList': []})
        self.send_point(point_D1)
        layer = sync_instance.projects[0].shears_todo_layer
        features = layer.features_by_name('D1')
        assert len(features) == 0

    def test_update_with_the_same_timestamp_is_skipped(self, sync_instance, point_D1):
        self.send_point(point_D1)
        key = 'creator'
        point_D1.update({key: 'Lukas'})
        self.send_point(point_D1)
        layer = sync_instance.projects[0].points_layer
        assert layer.feature_by_name('D1').attribute('tworca') == 'wojtek'
