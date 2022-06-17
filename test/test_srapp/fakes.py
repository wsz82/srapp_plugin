from typing import List, Any, Tuple

from database.data import IFeature, IPointFeature


class FakeFeature(IFeature):

    def __init__(self, local_names: List[str], fid: int, **kwargs):
        super().__init__(None)
        self._local_names = local_names
        self._fid = fid
        self._attrs = kwargs

    def fid(self) -> int:
        return self._fid

    def set_attributes(self, attrs: list):
        attrs_map = dict(zip(self._local_names, attrs))
        self._attrs = attrs_map

    def attribute(self, name: str) -> Any:
        return self._attrs.get(name)

    def attributes(self) -> list:
        return list(self._attrs.values())


class FakePointFeature(FakeFeature, IPointFeature):

    def __init__(self, local_names: List[str], fid: int, x: float, y: float, **kwargs):
        super().__init__(local_names, fid, **kwargs)
        self._x = x
        self._y = y

    def set_geometry(self, x: float, y: float):
        pass

    def set_spatial_index(self):
        pass

    def xy(self) -> Tuple[float, float]:
        return self._x, self._y