import datetime
from decimal import Decimal
from typing import *

from srapp_model.database import point
from srapp_model.database.borehole import Borehole, BoreholeProduct
from srapp_model.database.layer import Layer
from srapp_model.database.point import Point
from srapp_model.database.probe import Probe, ProbeProduct
from srapp_model.database.shear import TodoShear, ShearUnit
from srapp_model.database.water import DrilledWaterHorizon, SetWaterHorizon, Exudation
from srapp_model.model import m_project
from srapp_model.model.m_project import FieldType, IFieldCreator


class FakeFieldCreator(IFieldCreator[list]):

    def make_field(self, **kwargs) -> list:
        return []

    def get_field_type(self, field_type: FieldType) -> Any:
        return 'field type'


class TestFieldNumber:

    def test_point_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.points_fields(FakeFieldCreator())
        keys = point.LOCAL_TO_REMOTE.local_names()
        values = ['D1', 'Wojtek', Decimal('0.0'), 'PL-KRON86-NH', 'DONE', 'TODO', Decimal('6.0'), Decimal('3.0'), True,
                  'DPL', 'Adam', '999888777', 'Królik', 'nie po zmroku', datetime.datetime.now()]
        attributes = dict(zip(keys, values))
        p = Point(460893.31642737595, 488559.55227616336, attributes, [])
        attrs = p.attrs()
        assert len(attrs) == len(fields)

    def test_borehole_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.boreholes_fields(FakeFieldCreator())
        borehole = Borehole(['Wojtek S', 'Lukasz K'], 'Konin', 'AB1234', float('0.0'), 'WH')
        bp = BoreholeProduct('czas', '1', 'wojtek', borehole, [], [], [], [])
        attrs = bp.attrs()
        assert len(attrs) == len(fields)

    def test_todo_shears_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.shears_todo_fields(FakeFieldCreator())
        todo_shear = TodoShear('D1', float('1.5'))
        attrs = todo_shear.attrs()
        assert len(attrs) == len(fields)

    def test_layers_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.layers_fields(FakeFieldCreator())
        layer = Layer('D1', float('1.0'), 'Pg', 'I', 'T', 'czerwony', 'mw', '1|2', 'tw', float('0.5'), 'opis')
        attrs = layer.attrs()
        assert len(attrs) == len(fields)

    def test_drilled_water_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.drilled_water_fields(FakeFieldCreator())
        water = DrilledWaterHorizon('D1', 'I', float('1.7'), 60)
        attrs = water.attrs()
        assert len(attrs) == len(fields)

    def test_set_water_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.set_water_fields(FakeFieldCreator())
        water = SetWaterHorizon('D1', 'I', float('1.7'), 0, 60)
        attrs = water.attrs()
        assert len(attrs) == len(fields)

    def test_exudation_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.exudations_fields(FakeFieldCreator())
        water = Exudation('D1', '-', float('1.7'), 60)
        attrs = water.attrs()
        assert len(attrs) == len(fields)

    def test_probe_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.probes_fields(FakeFieldCreator())
        probe = Probe([], 'Konin', 'KJ2211', float('0.0'), 'DPL', float('0.1'), [])
        pp = ProbeProduct('czas', 'D1', 'Wojtek', probe, [])
        attrs = pp.attrs()
        assert len(attrs) == len(fields)

    def test_shears_number_of_attrs_equals_number_of_fields(self):
        fields = m_project.shear_unit_fields(FakeFieldCreator())
        shear_unit = ShearUnit('D1', float('1.3'), 0, '15')
        attrs = shear_unit.attrs()
        assert len(attrs) == len(fields)
