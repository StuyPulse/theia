
from dataclasses import dataclass

from wpimath.geometry import *

@dataclass(frozen=True)
class TagData:
    tid: int
    cam_to_tag: Pose3d
