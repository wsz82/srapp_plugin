import datetime
from typing import *

import pytest
from google.api_core.datetime_helpers import DatetimeWithNanoseconds

import database.borehole
from database import shear, probe, water, layer
from database.person import Person
from model import m_project
from srapp_model.database import data
from srapp_model.database import point
from srapp_model.database.borehole import BoreholeProduct, Borehole
from srapp_model.database.data import Data, IFeature
from srapp_model.database.layer import Layer
from srapp_model.database.point import Point
from srapp_model.database.probe import ProbeProduct, Probe, ProbeUnit
from srapp_model.database.shear import TodoShear, ShearUnit
from srapp_model.database.water import DrilledWaterHorizon, SetWaterHorizon, Exudation
from test_srapp.fakes import FakePointFeature


class FakeShearFeature(IFeature):
    def __init__(self, depth, index, value):
        super().__init__(None)
        self._depth = depth
        self._index = index
        self._value = value

    def attribute(self, attr: str):
        if attr == shear.SHEAR_DEPTH:
            return self._depth
        elif attr == shear.INDEX:
            return self._index
        elif attr == shear.VALUE:
            return self._value


class FakeProbeUnitFeature(IFeature):
    def __init__(self, index, value):
        super().__init__(None)
        self._index = index
        self._value = value

    def attribute(self, attr: str):
        if attr == probe.INDEX:
            return self._index
        elif attr == probe.VALUE:
            return self._value


class FakePersonFeature(IFeature):
    def __init__(self, name):
        super().__init__(None)
        self._name = name

    def attribute(self, attr: str):
        if attr == data.PERSON:
            return self._name


class FakeDrilledWaterFeature(IFeature):
    def __init__(self, horizon_value, depth, time):
        super().__init__(None)
        self._horizon_value = horizon_value
        self._depth = depth
        self._time = time

    def attribute(self, attr: str):
        if attr == water.HORIZON:
            return self._horizon_value
        elif attr == water.WATER_DEPTH:
            return self._depth
        elif attr == data.TIME:
            return self._time


class FakeExudationFeature(IFeature):

    def __init__(self, type, depth, time):
        super().__init__(None)
        self._type = type
        self._depth = depth
        self._time = time

    def attribute(self, attr: str):
        if attr == water.EXUDATION_TYPE:
            return self._type
        elif attr == water.EXUDATION_DEPTH:
            return self._depth
        elif attr == data.TIME:
            return self._time


class FakeTodoShearFeature(IFeature):
    def __init__(self, depth):
        super().__init__(None)
        self._depth = depth

    def attribute(self, attr: float):
        if attr == shear.SHEAR_DEPTH:
            return self._depth


class FakeLayerFeature(IFeature):
    def __init__(self, to: str, type: str, admixtures: str, interbeddings: str, color: str, moisture: str,
                 rollsNumber: str, soilState: str, sampling: str, desc: str):
        super().__init__(None)
        self.to = to
        self.type = type
        self.admixtures = admixtures
        self.interbeddings = interbeddings
        self.color = color
        self.moisture = moisture
        self.rollsNumber = rollsNumber
        self.soilState = soilState
        self.sampling = sampling
        self.desc = desc

    def attribute(self, attr: str):
        if attr == layer.TO:
            return self.to
        elif attr == layer.TYPE:
            return self.type
        elif attr == layer.ADMIXTURES:
            return self.admixtures
        elif attr == layer.INTERBEDDINGS:
            return self.interbeddings
        elif attr == layer.COLOR:
            return self.color
        elif attr == layer.MOISTURE:
            return self.moisture
        elif attr == layer.ROLLS_NUMBER:
            return self.rollsNumber
        elif attr == layer.SOIL_STATE:
            return self.soilState
        elif attr == layer.SAMPLING:
            return self.sampling
        elif attr == layer.DESCRIPTION:
            return self.desc


class TestParse:

    @pytest.fixture
    def raw_remote_time(self) -> DatetimeWithNanoseconds:
        return DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc)

    @pytest.fixture
    def remote_time(self) -> str:
        return Data.remote_time_to_local(
            DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc))

    @pytest.fixture
    def point_doc(self):
        return {'creator': 'wojtek',
                'boreholeDesignedDepth': '6.5',
                'height': 86.7,
                'x': 460797.19,
                'assignedPerformer': 'krolik',
                'probeStatus': 'TODO',
                'shearsToDoList': [],
                'isStakeoutDone': False,
                'probeDesignedDepth': '3.0',
                'probeType': 'DPL',
                'heightSystem': 'PL-KRON86-NH',
                'pointNumber': '3',
                'comments': None,
                'timestamp': None,
                'contact': '',
                'y': 488728.8,
                'owner': 'Andrzej Kowalski',
                'boreholeStatus': 'DONE'}

    @pytest.fixture
    def point_D1(self) -> dict:
        return {
            'x': 460797.19,
            'boreholeStatus': 'EMPTY',
            'heightSystem': 'PL-KRON86-NH',
            'assignedPerformer': 'wojtek',
            'height': 86.7,
            'owner': 'Józef',
            'pointNumber': 'D1',
            'probeDesignedDepth': '3.5',
            'timestamp': DatetimeWithNanoseconds(2022, 5, 31, 6, 17, 1, tzinfo=datetime.timezone.utc),
            'comments': None,
            'probeStatus': 'EMPTY',
            'creator': 'wojtek',
            'isStakeoutDone': False,
            'contact': '',
            'y': 488728.8,
            'shearsToDoList': [3.37, 5.1, 7],
            'probeType': 'DPL',
            'boreholeDesignedDepth': '7.0'
        }

    @pytest.fixture
    def borehole_D1(self) -> dict:
        return {
            "lastPerformer": "aplikacjametryka@gmail.com",
            "pointNumber": "D1",
            "bottomDepth": 8.0,
            "timestamp": DatetimeWithNanoseconds(2022, 4, 10, 16, 42, 56, 86000, tzinfo=datetime.timezone.utc),
            "point": {
                "drillType": "WHg",
                "persons": [
                    "Szpikowski Wojciech",
                    "Kowalski Jan"
                ],
                "startDepth": 0.0,
                "vehicleNumber": "PKN5544",
                "location": "Kramsk"
            },
            "borehole": {
                "vehicleNumber": "PKN5544",
                "location": "Kramsk",
                "persons": [
                    "Szpikowski Wojciech",
                    "Kowalski Jan"
                ],
                "drillType": "WH",
                "startDepth": ''
            },
            "layers": [
                {
                    "to": "1",
                    "interbeddings": "Π",
                    "sampling": "0.5",
                    "from": "0.00",
                    "moisture": "",
                    "desc": "opis1",
                    "color": "Brązowa",
                    "rollsNumber": "",
                    "soilState": "",
                    "admixtures": "Po",
                    "type": "Pog"
                },
                {
                    "color": "Ciemno-brązowa",
                    "admixtures": "Gπ",
                    "sampling": "",
                    "to": "2.3",
                    "rollsNumber": "5|6",
                    "desc": "opis2",
                    "interbeddings": "Gpz",
                    "soilState": "tpl",
                    "from": "1",
                    "moisture": "w/m",
                    "type": "Π"
                }
            ],
            "drilledWaterHorizons": [
                {
                    "depth": "0.8",
                    "timestamp": DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
                    "data": "II"
                },
                {
                    "timestamp": DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
                    "depth": "2.21",
                    "data": "III"
                },
                {
                    "data": "I",
                    "timestamp": DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
                    "depth": "0.4"
                }
            ],
            "setWaterHorizons": [
                {
                    "measurementPeriod": {
                        "days": 0,
                        "0": False,
                        "hours": 6,
                        "minutes": 0
                    },
                    "data": "II",
                    "timestamp": DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
                    "depth": "1.30"
                },
                {
                    "data": "I",
                    "measurementPeriod": {
                        "days": 1,
                        "hours": 0,
                        "0": False,
                        "minutes": 0
                    },
                    "depth": "0.40",
                    "timestamp": DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
                }
            ],
            "exudations": [
                {
                    "depth": "0.5",
                    "data": "1",
                    "timestamp": DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
                },
                {
                    "depth": "0.2",
                    "timestamp": DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
                    "data": "2"
                }
            ]
        }

    @pytest.fixture
    def probe_D1(self) -> dict:
        return {
            'timestamp': DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc),
            'shears': [
                {'depth': '1.6',
                 'torques': ['13', '24', '34', '56', '76', '87', '90', '100', '110', '90', '60', '50', '46', '45', '45',
                             '43', '43', '43']},
                {'depth': '2.7',
                 'torques': ['6', '7', '9', '11', '26', '34', '17', '15', '13', '13', '13', '13', '13', '13', '13',
                             '13', '13', '13']},
            ],
            'lastPerformer': 'aplikacjametryka@gmail.com',
            'pointNumber': 'D1',
            'probe': {
                'interval': '0.2',
                'probeType': 'DPL',
                'units': ['3', '5', '7', '5', '8', '12', '14', '16', '14', '13', '17', '18', '15', '18', '17', '19'],
                'location': 'Kramsk',
                'persons': ['Szpikowski Wojciech'],
                'vehicleNumber': 'PKN4836',
                'startDepth': 0.5
            }
        }

    def test_data_class_equality(self, point_D1):
        name = 'D1'
        s1 = TodoShear(name, float('3.37'))
        s2 = TodoShear(name, float(3.37))
        assert s1 == s2

    def test_remote_datetime_is_parsed_to_seconds_precision(self):
        remote = DatetimeWithNanoseconds(2022, 4, 10, 16, 42, 56, 86000, tzinfo=datetime.timezone.utc)
        parsed = Data.remote_time_to_local(remote)
        expected = str(datetime.datetime(2022, 4, 10, 18, 42, 56, tzinfo=datetime.timezone(datetime.timedelta(hours=2))))
        assert parsed == expected

    @pytest.mark.parametrize(
        "timestamp",
        [
            pytest.param(
                DatetimeWithNanoseconds(2022, 5, 4, 7, 0, 1, tzinfo=datetime.timezone.utc), id="with_timestamp"
            ),
            pytest.param(
                None, id="no_timestamp"
            ),
        ],
    )
    def test_point_is_parsed_from_remote(self, point_doc, timestamp):
        point_doc.update({data.TIME_REMOTE: timestamp})
        p = Point.from_dict(point_doc)
        assert p.x == 460797.19
        assert p.y == 488728.8
        assert p.shears_todo == []
        keys = point.LOCAL_TO_REMOTE.local_names()
        values = [Data.remote_time_to_local(timestamp), '3', 'wojtek', 86.7, 'PL-KRON86-NH', 'Zrobiony', 'Do zrobienia',
                  '6.5', '3.0',
                  False, 'DPL',
                  'Andrzej Kowalski', '', 'krolik', None]
        fields = dict(zip(keys, values))
        assert p.fields == fields

    def test_point_parsed_from_remote_has_attrs_in_order(self, point_doc):
        p = Point.from_dict(point_doc)
        keys = point.LOCAL_TO_REMOTE.local_names()
        fields_keys = list(p.fields.keys())
        for idx, key in enumerate(keys):
            assert fields_keys[idx] == key

    def test_point_is_parsed(self, point_D1):
        name = 'D1'
        time = Data.remote_time_to_local(DatetimeWithNanoseconds(2022, 5, 31, 6, 17, 1, tzinfo=datetime.timezone.utc))
        parsed = Point.from_dict(point_D1)
        shears_todo: List[TodoShear] = [
            TodoShear(name, float('3.37')),
            TodoShear(name, float('5.1')),
            TodoShear(name, float('7'))
        ]
        fields = OrderedDict([(data.TIME, time),
                              (data.NAME, 'D1'),
                              (point.CREATOR, 'wojtek'),
                              (point.HEIGHT, 86.7),
                              (point.HEIGHT_SYSTEM, 'PL-KRON86-NH'),
                              (point.BOREHOLE_STATE, ''),
                              (point.PROBE_STATE, ''),
                              (point.BOREHOLE_DEPTH, '7.0'),
                              (point.PROBE_DEPTH, '3.5'),
                              (point.STAKEOUT, False),
                              (point.PROBE_TYPE, 'DPL'),
                              (point.OWNER, 'Józef'),
                              (point.CONTACT, ''),
                              (point.ASSIGNED_PERFORMER, 'wojtek'),
                              (point.COMMENTS, None)])
        expected = Point(460797.19, 488728.8, fields, shears_todo)
        assert parsed == expected

    def test_borehole_is_parsed(self, borehole_D1, remote_time):
        name = 'D1'
        parsed = BoreholeProduct.from_dict(borehole_D1)
        time = Data.remote_time_to_local(
            DatetimeWithNanoseconds(2022, 4, 10, 16, 42, 56, 86000, tzinfo=datetime.timezone.utc))
        borehole = Borehole([Person(name, "Szpikowski Wojciech"), Person(name, "Kowalski Jan")], 'Kramsk', 'PKN5544', 0,
                            'WH')
        layers = [
            Layer(name, float('1'), "Pog", "Po", "Π", "Brązowa", '', '', '', float('0.5'), 'opis1'),
            Layer(name, float('2.3'), "Π", "Gπ", "Gpz", "Ciemno-brązowa", 'w/m', '5|6', 'tpl', None, 'opis2'),
        ]
        drilled_water = [
            DrilledWaterHorizon(name, 'II', float('0.80'), remote_time),
            DrilledWaterHorizon(name, 'III', float('2.21'), remote_time),
            DrilledWaterHorizon(name, 'I', float('0.40'), remote_time),
        ]
        set_water = [
            SetWaterHorizon(name, 'II', float('1.30'), remote_time, 360),
            SetWaterHorizon(name, 'I', float('0.40'), remote_time, 1440),
        ]
        exudations = [
            Exudation(name, '1', float('0.50'), remote_time),
            Exudation(name, '2', float('0.20'), remote_time),
        ]
        expected = BoreholeProduct(time, name, 'aplikacjametryka@gmail.com', borehole, layers, drilled_water, set_water,
                                   exudations)
        assert parsed == expected

    def test_probe_is_parsed(self, probe_D1, remote_time):
        name = 'D1'
        parsed = ProbeProduct.from_dict(probe_D1)
        units = [
            ProbeUnit(name, 0, '3'),
            ProbeUnit(name, 1, '5'),
            ProbeUnit(name, 2, '7'),
            ProbeUnit(name, 3, '5'),
            ProbeUnit(name, 4, '8'),
            ProbeUnit(name, 5, '12'),
            ProbeUnit(name, 6, '14'),
            ProbeUnit(name, 7, '16'),
            ProbeUnit(name, 8, '14'),
            ProbeUnit(name, 9, '13'),
            ProbeUnit(name, 10, '17'),
            ProbeUnit(name, 11, '18'),
            ProbeUnit(name, 12, '15'),
            ProbeUnit(name, 13, '18'),
            ProbeUnit(name, 14, '17'),
            ProbeUnit(name, 15, '19'),
        ]
        probe = Probe([Person(name, 'Szpikowski Wojciech')], 'Kramsk', 'PKN4836', float('0.5'), 'DPL', float('0.2'),
                      units)
        shear_units = [
            ShearUnit(name, 1.6, 0, '13'),
            ShearUnit(name, 1.6, 1, '24'),
            ShearUnit(name, 1.6, 2, '34'),
            ShearUnit(name, 1.6, 3, '56'),
            ShearUnit(name, 1.6, 4, '76'),
            ShearUnit(name, 1.6, 5, '87'),
            ShearUnit(name, 1.6, 6, '90'),
            ShearUnit(name, 1.6, 7, '100'),
            ShearUnit(name, 1.6, 8, '110'),
            ShearUnit(name, 1.6, 9, '90'),
            ShearUnit(name, 1.6, 10, '60'),
            ShearUnit(name, 1.6, 11, '50'),
            ShearUnit(name, 1.6, 12, '46'),
            ShearUnit(name, 1.6, 13, '45'),
            ShearUnit(name, 1.6, 14, '45'),
            ShearUnit(name, 1.6, 15, '43'),
            ShearUnit(name, 1.6, 16, '43'),
            ShearUnit(name, 1.6, 17, '43'),
            ShearUnit(name, 2.7, 0, '6'),
            ShearUnit(name, 2.7, 1, '7'),
            ShearUnit(name, 2.7, 2, '9'),
            ShearUnit(name, 2.7, 3, '11'),
            ShearUnit(name, 2.7, 4, '26'),
            ShearUnit(name, 2.7, 5, '34'),
            ShearUnit(name, 2.7, 6, '17'),
            ShearUnit(name, 2.7, 7, '15'),
            ShearUnit(name, 2.7, 8, '13'),
            ShearUnit(name, 2.7, 9, '13'),
            ShearUnit(name, 2.7, 10, '13'),
            ShearUnit(name, 2.7, 11, '13'),
            ShearUnit(name, 2.7, 12, '13'),
            ShearUnit(name, 2.7, 13, '13'),
            ShearUnit(name, 2.7, 14, '13'),
            ShearUnit(name, 2.7, 15, '13'),
            ShearUnit(name, 2.7, 16, '13'),
            ShearUnit(name, 2.7, 17, '13'),
        ]
        expected = ProbeProduct(remote_time, name, 'aplikacjametryka@gmail.com', probe, shear_units)
        assert parsed == expected

    def test_borehole_time_field_is_first_and_name_second(self, borehole_D1):
        time = Data.remote_time_to_local(
            DatetimeWithNanoseconds(2022, 4, 10, 16, 42, 56, 86000, tzinfo=datetime.timezone.utc))
        parsed = BoreholeProduct.from_dict(borehole_D1)
        attrs = parsed.attrs()
        assert attrs[0] == time
        assert attrs[1] == 'D1'

    def test_probe_time_field_is_first_and_name_second(self, probe_D1):
        time = Data.remote_time_to_local(
            DatetimeWithNanoseconds(2022, 3, 26, 18, 27, 26, 314000, tzinfo=datetime.timezone.utc))
        parsed = ProbeProduct.from_dict(probe_D1)
        attrs = parsed.attrs()
        assert attrs[0] == time
        assert attrs[1] == 'D1'

    def test_shears_are_parsed_to_remote(self):
        features = [
            FakeShearFeature(1.6, 17, '43'),
            FakeShearFeature(1.6, 0, '13'),
            FakeShearFeature(1.6, 1, '24'),
            FakeShearFeature(1.6, 15, '43'),
            FakeShearFeature(1.6, 2, '34'),
            FakeShearFeature(1.6, 3, '56'),
            FakeShearFeature(1.6, 11, '50'),
            FakeShearFeature(1.6, 13, '45'),
            FakeShearFeature(1.6, 8, '110'),
            FakeShearFeature(1.6, 4, '76'),
            FakeShearFeature(1.6, 5, '87'),
            FakeShearFeature(1.6, 6, '90'),
            FakeShearFeature(1.6, 16, '43'),
            FakeShearFeature(1.6, 7, '100'),
            FakeShearFeature(1.6, 9, '90'),
            FakeShearFeature(1.6, 14, '45'),
            FakeShearFeature(1.6, 10, '60'),
            FakeShearFeature(1.6, 12, '46'),
            FakeShearFeature(2.7, 0, '6'),
            FakeShearFeature(2.7, 1, '7'),
            FakeShearFeature(2.7, 2, '9'),
            FakeShearFeature(2.7, 3, '11'),
            FakeShearFeature(2.7, 4, '26'),
            FakeShearFeature(2.7, 5, '34'),
            FakeShearFeature(2.7, 6, '17'),
            FakeShearFeature(2.7, 7, '15'),
            FakeShearFeature(2.7, 8, '13'),
            FakeShearFeature(2.7, 9, '13'),
            FakeShearFeature(2.7, 10, '13'),
            FakeShearFeature(2.7, 11, '13'),
            FakeShearFeature(2.7, 12, '13'),
            FakeShearFeature(2.7, 13, '13'),
            FakeShearFeature(2.7, 14, '13'),
            FakeShearFeature(2.7, 15, '13'),
            FakeShearFeature(2.7, 16, '13'),
            FakeShearFeature(2.7, 17, '13'),
        ]
        parsed: dict = m_project._shear_units_list_map(features)
        expected = {
            'shears': [
                {'depth': '1.6',
                 'torques': ['13', '24', '34', '56', '76', '87', '90', '100', '110', '90', '60', '50', '46', '45', '45',
                             '43', '43', '43']
                 },
                {'depth': '2.7',
                 'torques': ['6', '7', '9', '11', '26', '34', '17', '15', '13', '13', '13', '13', '13', '13', '13',
                             '13', '13', '13']},
            ]
        }
        assert parsed == expected

    def test_probe_units_are_parsed_to_remote(self, probe_D1):
        features = [
            FakeProbeUnitFeature(14, '17'),
            FakeProbeUnitFeature(1, '5'),
            FakeProbeUnitFeature(2, '7'),
            FakeProbeUnitFeature(3, '5'),
            FakeProbeUnitFeature(0, '3'),
            FakeProbeUnitFeature(4, '8'),
            FakeProbeUnitFeature(5, '12'),
            FakeProbeUnitFeature(10, '17'),
            FakeProbeUnitFeature(6, '14'),
            FakeProbeUnitFeature(7, '16'),
            FakeProbeUnitFeature(8, '14'),
            FakeProbeUnitFeature(12, '15'),
            FakeProbeUnitFeature(9, '13'),
            FakeProbeUnitFeature(11, '18'),
            FakeProbeUnitFeature(13, '18'),
            FakeProbeUnitFeature(15, '19'),
        ]
        parsed = m_project._probe_units_list_map(features)
        expected = {'probe': {
            'units': ['3', '5', '7', '5', '8', '12', '14', '16', '14', '13', '17', '18', '15', '18', '17', '19'],
        }}
        assert parsed == expected

    def test_persons_are_parsed_to_remote(self):
        features = [
            FakePersonFeature('Wojtek'),
            FakePersonFeature('Wojtek Szpikowski'),
            FakePersonFeature('Zygmunt Brzęczyszczykiewicz'),
        ]
        parsed = m_project._persons_list_map(features)
        expected = {'point': {
            'persons': ['Wojtek', 'Wojtek Szpikowski', 'Zygmunt Brzęczyszczykiewicz'],
        }}
        assert parsed == expected

    def test_water_horizons_are_parsed_to_remote(self, borehole_D1, raw_remote_time):
        features = [
            FakeDrilledWaterFeature('II', '0.80', raw_remote_time),
            FakeDrilledWaterFeature('III', '2.21', raw_remote_time),
            FakeDrilledWaterFeature('I', '0.40', raw_remote_time),
        ]
        parsed = m_project._water_horizons_map(features)
        map = borehole_D1.get(database.borehole.DRILLED_WATER_HORIZONS_REMOTE)
        expected = {
            database.borehole.DRILLED_WATER_HORIZONS_REMOTE: map
        }
        assert parsed == expected

    def test_exudations_are_parsed_to_remote(self, borehole_D1, raw_remote_time):
        features = [
            FakeExudationFeature('1', '0.50', raw_remote_time),
            FakeExudationFeature('2', '0.20', raw_remote_time),
        ]
        parsed = m_project._exudations_list(features)
        map = borehole_D1.get(database.borehole.EXUDATIONS_REMOTE)
        expected = {
            database.borehole.EXUDATIONS_REMOTE: map
        }
        assert parsed == expected

    def test_layers_are_parsed_to_remote(self, borehole_D1):
        features = [
            FakeLayerFeature('1', 'Pog', 'Po', 'Π', 'Brązowa', '', '', '', '0.5', 'opis1'),
            FakeLayerFeature('2.3', 'Π', 'Gπ', 'Gpz', 'Ciemno-brązowa', 'w/m', '5|6', 'tpl', None, 'opis2'),
        ]
        parsed = m_project._layers_map(features)
        expected = {"layers": [
            {
                "to": '1.0',
                "interbeddings": "Π",
                "sampling": '0.5',
                "moisture": "",
                "desc": "opis1",
                "color": "Brązowa",
                "rollsNumber": "",
                "soilState": "",
                "admixtures": "Po",
                "type": "Pog"
            },
            {
                "color": "Ciemno-brązowa",
                "admixtures": "Gπ",
                "sampling": '',
                "to": '2.3',
                "rollsNumber": "5|6",
                "desc": "opis2",
                "interbeddings": "Gpz",
                "soilState": "tpl",
                "moisture": "w/m",
                "type": "Π"
            }
        ]
        }
        assert parsed == expected

    def test_todo_shears_are_parsed_to_remote(self, point_D1):
        features = [
            FakeTodoShearFeature(3.37),
            FakeTodoShearFeature(5.1),
            FakeTodoShearFeature(7),
        ]
        parsed = m_project._todo_shears_list(features)
        map = point_D1.get(point.SHEARS_TODO_LIST_REMOTE)
        expected = {
            point.SHEARS_TODO_LIST_REMOTE: map
        }
        assert parsed == expected

    def test_point_is_parsed_to_remote(self, point_D1):
        expected_data = {
            'boreholeStatus': 'EMPTY',
            'heightSystem': 'PL-KRON86-NH',
            'assignedPerformer': 'wojtek',
            'height': 86.7,
            'owner': 'Józef',
            'pointNumber': 'D1',
            'probeDesignedDepth': '3.5',
            'timestamp': DatetimeWithNanoseconds(2022, 5, 31, 6, 17, 1, tzinfo=datetime.timezone.utc),
            'comments': '',
            'probeStatus': 'EMPTY',
            'creator': 'wojtek',
            'isStakeoutDone': False,
            'contact': '',
            'probeType': 'DPL',
            'boreholeDesignedDepth': '7.0',
            'x': 0,
            'y': 0,
        }
        point_map = {
            data.TIME: DatetimeWithNanoseconds(2022, 5, 31, 6, 17, 1, tzinfo=datetime.timezone.utc),
            data.NAME: 'D1',
            point.CREATOR: 'wojtek',
            point.HEIGHT: 86.7,
            point.HEIGHT_SYSTEM: 'PL-KRON86-NH',
            point.BOREHOLE_STATE: '',
            point.PROBE_STATE: '',
            point.BOREHOLE_DEPTH: '7.0',
            point.PROBE_DEPTH: '3.5',
            point.STAKEOUT: False,
            point.PROBE_TYPE: 'DPL',
            point.OWNER: 'Józef',
            point.CONTACT: '',
            point.ASSIGNED_PERFORMER: 'wojtek',
            point.COMMENTS: None
        }
        features = [
            FakePointFeature(point.LOCAL_TO_REMOTE.local_names(), 1, 0, 0, **point_map),
        ]
        parsed = m_project._points_map(features)
        expected = {
            'D1': expected_data
        }
        assert parsed == expected

        # todo test parse boreholes, parse probes
