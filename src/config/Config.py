"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

import numpy
import numpy.typing
from dataclasses import dataclass, field

@dataclass
class LocalConfig:
    device_name: str = ""
    server_ip: str = ""
    team_number: int = 0
    stream_port: int = 5802
    detection_dictionary: any = None
    calibration_dictionary: any = None
    aruco_parameters: any = None
    charuco_board: any = None

    camera_matrix: numpy.typing.NDArray[numpy.float64] = None
    distortion_coefficient: numpy.typing.NDArray[numpy.float64] = None

@dataclass
class RemoteConfig:
    camera_id: int = 0
    camera_resolution_width: int = 1600
    camera_resolution_height: int = 1200
    camera_auto_exposure: int = 1
    camera_exposure: int = 50
    camera_gain: int = 0
    camera_brightness: int = 0
    fiducial_size: float = 0.15
    # [id, x, y, z, pitch, roll, yaw]: [_, m, m, m, deg, deg, deg]
    fiducial_layout: list = field(default_factory=list)
    # [x, y, z, pitch, roll, yaw]: [m, m, m, deg, deg, deg]
    camera_offset: list = field(default_factory=list)

@dataclass
class Config:
    local: LocalConfig
    remote: RemoteConfig