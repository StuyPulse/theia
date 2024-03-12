"""
Copyright (c) 2023-2024 Ivan Chen, StuyPulse

Use of this source code is governed by an MIT-style
license that can be found in the LICENSE file or at
https://opensource.org/license/MIT.
"""

"""
cv2 library provides useful functions and methods for working with images
numpy provides a wide variety of mathematical operations on arrays
"""
import cv2
import numpy

"""
Config allows us to connect to the camera and other information locally or remotely.
- LocalConfig sets up misallenous information
- RemoteConfig sets up information about the camera
"""
from config.Config import Config

class Annotate:
    """
    Initial definition of the functions.
    Raises exceptions if the functions are not implmented
    """

    def __init__(self):
        raise NotImplementedError
    
    def annotate(self, image, config: Config):
        raise NotImplementedError

    @classmethod
    def drawCube(self, frame, image_points:list):
        """
        The frame parameter provides the initial image, where cv2 will perform operations on
        The image_points parameter is a list containing the points in the image to perform operations on.
        drawCube(...) draws contours and lines based on image_points and returns the edited image
        """

        #Reshapes the array to a 2D array where the 2nd dimension has a size of 2
        image_points = numpy.int32(image_points).reshape(-1,2)

        #cv2 draws contours by extracting the image points and draws ALL the contours.
        #contours are outlines/boundaries of objects in an image
        frame = cv2.drawContours(frame, [image_points[:4]], -1, (0,255,0), 3)

        #runs a nested for loop to draw the lines between every pair of image points (given 2 points, exactly one line connects them both)
        for i, j in zip(range(4),range(4,8)):
            frame = cv2.line(frame, tuple(image_points[i]), tuple(image_points[j]), (255), 3)
        
        frame = cv2.drawContours(frame, [image_points[4:]], -1, (0,0,255), 3)

        return frame
    
class AnnotateFiducials(Annotate):
    """
    Annotates the AprilTags using the class previously defined.
    Returns the annotated AprilTag image
    """

    fiducial_size = 0.0
    axis = numpy.array([])

    def __init__(self):
        pass

    def annotate(self, image, rvecs, tvecs, fps, fpt, config: Config):
        if config.remote.fiducial_size != self.fiducial_size: 
            self.fiducial_size = config.remote.fiducial_size    #sets the correct AprilTag size based on information from Config
            #Sets the 2nd dimension arrays to the maximum boundaries (the outer edges of the AprilTag) 
            self.axis = numpy.float32([[-self.fiducial_size/2,-self.fiducial_size/2,0], [self.fiducial_size/2,-self.fiducial_size/2,0],
                   [self.fiducial_size/2,self.fiducial_size/2,0], [-self.fiducial_size/2,self.fiducial_size/2,0],
                   [-self.fiducial_size/2,-self.fiducial_size/2,self.fiducial_size],[self.fiducial_size/2,-self.fiducial_size/2,self.fiducial_size],
                   [self.fiducial_size/2,self.fiducial_size/2,self.fiducial_size],[-self.fiducial_size/2,self.fiducial_size/2,self.fiducial_size]
                  ])

        """
        Nested for loop through the rotation and translation vectors.
        The rotation vetors are converted to a Rodrigues rotation vector (compact representation of a 3D rotation), which is more efficient and easier to manipulate
        The 3D image points are projected into a 2D image plane
        The new 2D image plane is annotated
        The annotated 2D image is returned.
        """
        for rvec, tvec in zip(rvecs, tvecs):
            rvec, _ = cv2.Rodrigues(rvec)
            image_points, _ = cv2.projectPoints(self.axis, rvec, tvec, config.local.camera_matrix, config.local.distortion_coefficient)
            image = self.drawCube(image, image_points)
        cv2.putText(image, "FPS: " + str(round(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(image, "FPT: " + str(round(fpt * 1000)) + "ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        return image