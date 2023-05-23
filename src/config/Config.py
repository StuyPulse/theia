import numpy
import numpy.typing
from dataclasses import dataclass, field

@dataclass
class LocalConfig:
    device_id: str = ""
    server_ip: str = ""
    stream_port: int = 5802
    calibrated: bool = False
    fiducial_size: float = 0
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
    fiducial_layout: any = field(default_factory=list)

@dataclass
class Config:
    local: LocalConfig
    remote: RemoteConfig