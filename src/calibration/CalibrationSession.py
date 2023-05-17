from datetime import datetime
import cv2
import numpy
import json
from typing import List

from config.Config import Config

class CalibrationSession:
    all_corners: List[numpy.ndarray] = []
    all_ids: List[numpy.ndarray] = []
    image_size: any = None
    detector: any = None
    number_of_images: int = 0

    def __init__(self, config: Config) -> None:
        self.config = config
        self.detector = cv2.aruco.CharucoDetector(config.local.charuco_board)
    
    def process(self, image) -> int:
        charuco_corners, charuco_ids, marker_corners, marker_ids = self.detector.detectBoard(image)

        if charuco_corners is not None and charuco_ids is not None:
            if number_of_images == 0: self.image_size = (image.shape[0], image.shape[1])
            self.all_corners.append(charuco_corners)
            self.all_ids.append(charuco_ids)
            print("Saved calibration image")
            number_of_images += 1
        
        return number_of_images
    
    def calibrate(self) -> bool:
        retval, camera_matrix, distortion_coefficient, rvecs, tvecs = cv2.aruco.calibrateCameraCharuco(self.all_corners, self.all_ids, self.config.local.charuco_board, self.image_size, None, None)
        
        if retval:
            output = {
                "number_of_images": self.number_of_images,
                "timestamp": str(datetime.now()),
                "camera_matrix": camera_matrix.tolist(),
                "distortion_coefficient": distortion_coefficient.tolist()
            }
            try:
                with open(self.config.local.calibration_file, "w") as file:
                    file.write(json.dumps(output, indent=4))
            except:
                print("Failed to write calibration data to " + self.config.local.calibration_file)
                return False
            
            print("Wrote calibration data to " + self.config.local.calibration_file)
            return True
        
        return False
