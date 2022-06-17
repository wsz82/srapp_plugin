import pytest

from srapp_model.model import LocalToRemote


class TestLocalToRemote:

    @pytest.fixture
    def map(self):
        return LocalToRemote([
            ('nazwa', 'pointNumber'),
            ('tworca', 'creator'),
            ('wysokosc', 'height'),
            ('ukl_wys', 'heightSystem'),
            ('st_wierc', 'boreholeStatus'),
            ('st_sond', 'probeStatus'),
            ('gl_wierc', 'boreholeDesignedDepth'),
            ('gl_sond', 'probeDesignedDepth'),
            ('wytycz', 'isStakeoutDone'),
            ('typ_sond', 'probeType'),
            ('wlasc', 'owner'),
            ('kontakt', 'contact'),
            ('wykon', 'assignedPerformer'),
            ('koment', 'comments'),
            ('czas', 'timestamp'),
        ])

    def test_find_key_by_value(self, map):
        val = 'boreholeDesignedDepth'
        key = map.key(val)
        assert key == 'gl_wierc'