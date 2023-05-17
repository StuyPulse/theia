import cv2
from datetime import datetime
from threading import Thread

from config.Config import Config

class Capture:
    def __init__(self) -> None:
        raise NotImplementedError
        
    def getFrame(self, config: Config) -> None:
        raise NotImplementedError
    
    def release(self) -> None:
        raise NotImplementedError
    
    @classmethod
    def configChanged(cls, config_a: Config, config_b: Config) -> bool:
        if config_a == None and config_b == None:
            return False
        if config_a == None or config_b == None:
            return True

        remote_a = config_a.remote_config
        remote_b = config_b.remote_config

        return remote_a.camera_id != remote_b.camera_id or remote_a.camera_resolution_width != remote_b.camera_resolution_width or remote_a.camera_resolution_height != remote_b.camera_resolution_height or remote_a.camera_auto_exposure != remote_b.camera_auto_exposure or remote_a.camera_exposure != remote_b.camera_exposure or remote_a.camera_gain != remote_b.camera_gain
                
class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.stream.read()

        self.stopped = False

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
    
    def set(self, propId, value):
        self.stream.set(propId, value)

    def update(self):
        while True:
            if self.stopped:
                return

            self.grabbed, self.frame = self.stream.read()
    
    def read(self):
        return self.frame
    
    def release(self):
        self.stopped = True
                
class MockCapture(Capture):
    def __init__(self) -> None:
        pass
        
    def getFrame(self, config: Config):
        pass
        
    def release(self) -> None:
        pass

class DefaultCapture(Capture):
    
    video = None
    last_config: Config = None

    def __init__(self) -> None:
        pass
    
    def getFrame(self, config: Config):
        if self.video != None and self.configChanged(self.last_config, config):
            print(str(datetime.now()) + " - Restarting video capture after configuration change")
            self.video.release()
            self.video = None

        if self.video == None:
            print(str(datetime.now()) + " - Starting video capture")
            # self.video = cv2.VideoCapture(config.remote_config.camera_id)
            self.video = WebcamVideoStream(src=config.remote_config.camera_id).start()
            self.video.set(cv2.CAP_PROP_FRAME_WIDTH, config.remote_config.camera_resolution_width)
            self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, config.remote_config.camera_resolution_height)
            self.video.set(cv2.CAP_PROP_FPS, 60)
            self.video.set(cv2.CAP_PROP_AUTO_EXPOSURE, config.remote_config.camera_auto_exposure)
            self.video.set(cv2.CAP_PROP_EXPOSURE, config.remote_config.camera_exposure)
            self.video.set(cv2.CAP_PROP_GAIN, config.remote_config.camera_gain)
        
        self.last_config = config

        return self.video.read()
    
    def release(self) -> None:
          print(str(datetime.now()) + " - Releasing video capture")
          if self.video != None: self.video.release()
    
    
