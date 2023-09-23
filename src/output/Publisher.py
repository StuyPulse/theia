import ntcore
from typing import Union
import numpy.typing

from config.Config import Config

class Publisher:

    def __init__(self):
        raise NotImplementedError

    def send(self, config: Config, timestamp: float, fps: Union[int, None], pose):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError

class NTPublisher:

    fps_pub: ntcore.FloatPublisher
    pose_pub: ntcore.DoubleArrayPublisher

    def __init__(self, config: Config):

        instance = ntcore.NetworkTableInstance.getDefault()
        instance.setServerTeam(config.local.team_number)
        instance.setServer(config.local.server_ip, ntcore.NetworkTableInstance.kDefaultPort4)
        instance.startClient4(config.local.device_name)
        table = instance.getTable("/" + config.local.device_name + "/output")

        self.fps_pub = table.getFloatTopic("fps").publish()
        self.fps_pub.setDefault(-1)
        self.pose_pub = table.getDoubleArrayTopic("robot_pose").publish(ntcore.PubSubOptions(keepDuplicates=True, pollStorage=10))
        self.pose_pub.setDefault([])
        pass

    def send(self, pose: numpy.typing.NDArray[numpy.float64], fps: Union[float, None], latency: Union[float, None]):
        
        if fps is not None:
            self.fps_pub.set(fps)

        if pose is not None and latency is not None:
            pose = numpy.insert(pose, pose.size, latency * 1000)
            self.pose_pub.set(pose, ntcore._now())
        else: 
            self.pose_pub.set([], ntcore._now())
        print("Sent: ", pose, fps)

    def close(self):
        self.fps_pub.close()
        self.pose_pub.close()
