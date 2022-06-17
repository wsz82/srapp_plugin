import dataclasses
from typing import *

from database.data import PointData
from model import LocalToRemote
from srapp_model.database import data
from srapp_model.database.data import Data
from srapp_model.database.shear import TodoShear

POINT_X = 'x'
POINT_Y = 'y'
SHEARS_TODO_LIST_REMOTE = 'shearsToDoList'

CREATOR = 'tworca'
HEIGHT = 'wysokosc'
HEIGHT_SYSTEM = 'ukl_wys'
BOREHOLE_STATE = 'st_wierc'
PROBE_STATE = 'st_sond'
BOREHOLE_DEPTH = 'gl_wierc'
PROBE_DEPTH = 'gl_sond'
STAKEOUT = 'wytycz'
PROBE_TYPE = 'typ_sond'
OWNER = 'wlasc'
CONTACT = 'kontakt'
ASSIGNED_PERFORMER = 'wykon'
COMMENTS = 'koment'

CREATOR_REMOTE = 'creator'
HEIGHT_REMOTE = 'height'
HEIGHT_SYSTEM_REMOTE = 'heightSystem'
BOREHOLE_STATE_REMOTE = 'boreholeStatus'
PROBE_STATE_REMOTE = 'probeStatus'
BOREHOLE_DEPTH_REMOTE = 'boreholeDesignedDepth'
PROBE_DEPTH_REMOTE = 'probeDesignedDepth'
STAKEOUT_REMOTE = 'isStakeoutDone'
PROBE_TYPE_REMOTE = 'probeType'
OWNER_REMOTE = 'owner'
CONTACT_REMOTE = 'contact'
ASSIGNED_PERFORMER_REMOTE = 'assignedPerformer'
COMMENTS_REMOTE = 'comments'

LOCAL_TO_REMOTE: LocalToRemote[str, str] = LocalToRemote([
    (data.TIME, data.TIME_REMOTE),
    (data.NAME, data.NAME_REMOTE),
    (CREATOR, CREATOR_REMOTE),
    (HEIGHT, HEIGHT_REMOTE),
    (HEIGHT_SYSTEM, HEIGHT_SYSTEM_REMOTE),
    (BOREHOLE_STATE, BOREHOLE_STATE_REMOTE),
    (PROBE_STATE, PROBE_STATE_REMOTE),
    (BOREHOLE_DEPTH, BOREHOLE_DEPTH_REMOTE),
    (PROBE_DEPTH, PROBE_DEPTH_REMOTE),
    (STAKEOUT, STAKEOUT_REMOTE),
    (PROBE_TYPE, PROBE_TYPE_REMOTE),
    (OWNER, OWNER_REMOTE),
    (CONTACT, CONTACT_REMOTE),
    (ASSIGNED_PERFORMER, ASSIGNED_PERFORMER_REMOTE),
    (COMMENTS, COMMENTS_REMOTE),
])


@dataclasses.dataclass(frozen=True)
class Point(PointData):
    fields: OrderedDict[str, Any]
    shears_todo: List[TodoShear]

    def local_to_remote(self) -> LocalToRemote[str, str]:
        return LOCAL_TO_REMOTE

    def attrs(self):
        return list(self.fields.values())

    @staticmethod
    def from_dict(doc_map: dict) -> 'Point':
        name = doc_map.get(data.NAME_REMOTE)
        if not name:
            return None
        x = doc_map.get(POINT_X)
        y = doc_map.get(POINT_Y)
        fields = OrderedDict()
        for local_name, remote_name in LOCAL_TO_REMOTE.items():
            fields.update({local_name: doc_map.get(remote_name)})
        raw_remote_time = fields.get(data.TIME)
        time = Data.remote_time_to_local(raw_remote_time)
        fields.update({data.TIME: time})
        todo_shear_depths = doc_map.get(SHEARS_TODO_LIST_REMOTE, [])
        todo_shears = [TodoShear(name, float(shear_depth)) for shear_depth in todo_shear_depths]
        return Point(x, y, fields, todo_shears)
