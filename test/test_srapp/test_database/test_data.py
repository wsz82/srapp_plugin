from database.data import IFeature


class FakeFeature(IFeature):
    def __init__(self, fid):
        super().__init__(None)
        self._fid = fid

    def fid(self) -> int:
        return self._fid


def test_feature_equals():
    feat1 = FakeFeature(1)
    feat2 = FakeFeature(1)
    assert feat1 == feat2


def test_feature_not_equals():
    feat1 = FakeFeature(1)
    feat2 = FakeFeature(2)
    assert feat1 != feat2


def test_feature_removed_from_list():
    feat1 = FakeFeature(1)
    feats = [feat1]
    feat2 = FakeFeature(1)
    feats.remove(feat2)
    assert len(feats) == 0
