import dataclasses
from decimal import Decimal

from .data import Data
from typing import List
from .shear import TodoShear

from qgis._core import QgsFeature, QgsGeometry, QgsPointXY, QgsSpatialIndex

NAME = 'nazwa'
CREATOR = 'tworca'
HEIGHT = 'wysokosc'
HEIGHT_SYS = 'ukl_wys'
BOREHOLE_STATE = 'st_wierc'
PROBE_STATE = 'st_sond'
BOREHOLE_DEPTH = 'gl_wierc'
PROBE_DEPTH = 'gl_sond'
IS_STAKEOUT = 'wytycz'
PROBE_TYPE = 'typ_sond'
OWNER = 'wlasc'
CONTACT = 'kontakt'
ASSIGNED_PERFORMER = 'wykon'
COMMENT = 'koment'


@dataclasses.dataclass(frozen=True)
class Point(Data):
    x: float
    y: float
    pointNumber: str
    creator: str
    height: Decimal
    heightSystem: str
    boreholeStatus: str
    probeStatus: str
    boreholeDesignedDepth: str
    probeDesignedDepth: str
    isStakeoutDone: bool
    probeType: str
    owner: str
    contact: str
    assignedPerformer: str
    comments: str
    shearsToDoList: List[TodoShear]

    def attrs(self):
        return [
            self.pointNumber,
            self.creator,
            self.height,
            self.heightSystem,
            self.boreholeStatus,
            self.probeStatus,
            self.boreholeDesignedDepth,
            self.probeDesignedDepth,
            self.isStakeoutDone,
            self.probeType,
            self.owner,
            self.contact,
            self.assignedPerformer,
            self.comments
        ]

    @staticmethod
    def from_dict(doc_map) -> 'Point':
        name = doc_map.get('pointNumber')
        if not name:
            return None
        x = doc_map.get('x')
        y = doc_map.get('y')
        creator = doc_map.get('creator')
        height = doc_map.get('height')
        height_system = doc_map.get('heightSystem')
        borehole_status = doc_map.get('boreholeStatus')
        probe_status = doc_map.get('probeStatus')
        borehole_designed_depth = doc_map.get('boreholeDesignedDepth')
        probe_designed_depth = doc_map.get('probeDesignedDepth')
        is_stakeout_done = doc_map.get('isStakeoutDone')
        probe_type = doc_map.get('probeType')
        owner = doc_map.get('owner')
        contact = doc_map.get('contact')
        assigned_performer = doc_map.get('assignedPerformer')
        comments = doc_map.get('comments')
        todo_shear_depths = doc_map.get('shearsToDoList')
        todo_shears = [TodoShear(name, shear_depth) for shear_depth in todo_shear_depths]
        return Point(x, y, name, creator, height, height_system, borehole_status, probe_status,
                     borehole_designed_depth, probe_designed_depth, is_stakeout_done, probe_type, owner,
                     contact, assigned_performer, comments, todo_shears)

    @staticmethod
    def from_feature(feat: QgsFeature, shears_todo: List[TodoShear]) -> 'Point':
        geometry = feat.geometry()
        p = geometry.asPoint()
        x = p.x()
        y = p.y()
        return Point(x, y,
                     Point.get_attribute_value(feat, NAME),
                     Point.get_attribute_value(feat, CREATOR),
                     Point.get_attribute_value(feat, HEIGHT),
                     Point.get_attribute_value(feat, HEIGHT_SYS),
                     Point.get_attribute_value(feat, BOREHOLE_STATE),
                     Point.get_attribute_value(feat, PROBE_STATE),
                     Point.get_attribute_value(feat, BOREHOLE_DEPTH),
                     Point.get_attribute_value(feat, PROBE_DEPTH),
                     Point.get_attribute_value(feat, IS_STAKEOUT),
                     Point.get_attribute_value(feat, PROBE_TYPE),
                     Point.get_attribute_value(feat, OWNER),
                     Point.get_attribute_value(feat, CONTACT),
                     Point.get_attribute_value(feat, ASSIGNED_PERFORMER),
                     Point.get_attribute_value(feat, COMMENT),
                     shears_todo
                     )

    def to_feature(self) -> QgsFeature:
        feat = super(Point, self).to_feature()
        feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.x, self.y)))
        index = QgsSpatialIndex()
        index.addFeature(feat)
        return feat
