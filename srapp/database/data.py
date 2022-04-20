import dataclasses

from PyQt5.QtCore import QVariant
from qgis._core import QgsFeature


@dataclasses.dataclass(frozen=True)
class Data:

    def attr_map(self, feat_id):
        attr = self.attrs()
        return {feat_id: {i + 1: val for i, val in enumerate(attr)}}

    def to_feature(self) -> QgsFeature:
        feat = QgsFeature()
        attrs: list = self.attrs()
        attrs.insert(0, None)
        feat.setAttributes(attrs)
        return feat

    def attrs(self):
        """Layer database"""
        raise NotImplementedError

    @staticmethod
    def get_attribute_value(feature: QgsFeature, name: str):
        attribute = feature.attribute(name)
        return attribute if not isinstance(attribute, QVariant) else None
