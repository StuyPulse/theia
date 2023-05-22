import ntcore
from config.Config import Config

class Publisher:
    def send(self, config: Config, timestamp: float, fps: int, pose):
        raise NotImplementedError

class NTPublisher:

    init_complete: bool = False
    pose_pub: ntcore.DoubleArrayPublisher
    fps_pub: ntcore.IntegerPublisher

    def send(self, config: Config, timestamp: float, fps: int, pose):
        if not self.init_complete:
            table = ntcore.NetworkTableInstance.getDefault().getTable("/" + config.local.device_id + "/output")
            self.pose_pub = table.getDoubleArrayTopic("robot_pose").publish([])
            self.fps_pub = table.getIntegerTopic("fps").publish(0)
        
        if fps is not None:
            self.fps_pub.set(fps)
        if pose is not None:
            self.pose_pub.set(pose)
