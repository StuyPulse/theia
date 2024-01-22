# Theia

Theia aims to be a plug-and-play visual localization solution using the ArUco marker (aka fiducial) system and transfer the data using the NetworkTables communication system. ArUco markers are a popular choice for camera-based augmented reality or localization applications and can be utilized for determining the position and orientation of objects in a camera's field of view. 

Theia is able to detect ArUco markers within a camera's viewport and compute the relative positions of each marker to the camera using the SolvePnP algorithm. Combining this with knowledge of the absolute position of each marker on the environment, we can derive the absolute position of the camera within the environment with high accuracy and precision. 

## Table of Contents

- [Class Breakdown](#class-breakdown)
- [Installation](#installation)
- [Usage](#usage)
- [Calibration](#calibration)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Class Breakdown

`__init__.py`: Primary file of the project. Initialzes all components of the project and contains the primary loop.

### pipeline

`Capture.py`: Captures camera feed in a separate thread from the primary thread and returns individual frames on request.

`Detector.py`: Processes images using the ArUco detection algorithm to detect ArUco markers and returns the corner and id data of each detected marker.

`PoseEstimator.py`: Processes images using the SolvePnP (SquarePnP) algorithm to derive and output the absolute position of the robot in the environment.

### output

`Annotate.py`: Annotates images by drawing cubes representing the position of each tag in the image and writes FPS (frames per second) and PT (processing time) information onto the image.

`Publisher.py`: Publishes robot pose and FPS data to the NetworkTables.

`Stream.py`: Streams the processed camera feed to an HTTP server hosted on the device.

### config

`Config.py`: Stores the configuration information of the system.

`ConfigManager.py`: Reads configuration data from configuration files stored locally on the device in `src/config/data` and from NetworkTables.

## Installation

To set up the project on a headless Linux devices:

1. Download the installation script ([`install.sh`]()) in this repository.
    - `wget https://raw.githubusercontent.com/stuypulse/theia/main/install.sh -O install.sh`
2. Give the downloaded .sh file execute permissions.
    - `sudo chmod -x install.sh`
3. Run the script. This will automatically handle the download of the project, along with any of its dependancies and set up a `systemd` service to automatically execute the script on startup. 
    - `sudo ./install.sh`
4. Reboot the coprocessor.
    - `sudo reboot now`

To set up the project for development:

1. Clone the project repository.
    - `git clone https://github.com/stuypulse/theia.git`
2. Install the project dependancies.
    - `pip install -r requirements.txt`
3. Run the project.

## Usage

For headless Linux devices:

- To setup the project, see the [installation](#installation) section.
- To manually run the main project: `python3 src/__init__.py`
- To trigger manual calibration (only if you have images stored in `/captures`): `python3 manual_calibration.py`

*Note that the manual image snapshot capture script will not work as intended since they were designed with the usage of the CV2 window.*

For Linux, Windows, or MacOS devices:

- To run the main project: `python3 src/__init__.py`
- To manually capture image frames: `python3 capture_images.py`
- To manually calibrate the camera: `python3 manual_calibration.py`
- To generate a ChArUco board: `python3 charuco_board_gen.py`
- To generate ArUco markers (as pdfs): `python3 aruco_marker_gen.py`

## Calibration

Calibration or camera calibration is the process used to derive intrinsic information about the camera, such as the focal length, optical center point, and distortion coefficients. This information is used to correct for the distortion of the camera lens and to accurately detect markers in each frame of the camera stream. The calibration process will return two values, an array of camera matrix values and an array of distortion coefficients.

```python
camera_matrix = [[fx, 0, cx],
                 [0, fy, cy],
                 [0,  0,  1]]
```
Where `fx` and `fy` are the focal lengths of the camera in the x and y directions, respectively, and `cx` and `cy` are the coordinates of the optical center of the camera.

```python
distortion_coefficients = [k1, k2, p1, p2, k3]
```
Where `k1`, `k2`, and `k3` are the radial distortion coefficients and `p1` and `p2` are the tangential distortion coefficients.

### Calibration Process

1. Print out the ChArUco board included in the base directory of this project.
2. Trigger the calibration process. 
    - You may either utilize the manual calibration script seperately or the NetworkTables interface to trigger the calibration process in the main project.
3. Capture images of the ChArUco board from various angles and distances. The more images captured, the more accurate the calibration will be.
4. If the calibration process is successful, the calibration file will be saved in the `src/config/data/` directory.

### Output File

The calibration process will output a file named `calibration.json` in the `src/config/data` directory. This file contains the following:

- `number_of_images`: The number of images used for calibration.
- `timestamp`: The timestamp of the calibration session.
- `resolution`: The resolution of the images used for calibration.
- `camera_matrix`: The camera matrix values.
- `distortion_coefficients`: The distortion coefficients.

## Configuration

All of the values defined below can be accessed through the `Config` class in the `Config.py` file.

The `config.json` file contains various parameters that can be adjusted but not normally tuned. These parameters are:

- `device_name`: The name of the camera, which also determines the NetworkTable table name.
- `team_number`: The team number of the robot. The team number also determines the IP address of the NetworkTable server.
- `stream_port`: The port of the HTTP stream.
- `calibrated`: Whether the camera has been calibrated or not. If the camera has not been calibrated, the calibration process will be triggered on startup.
- `detection_dictionary`: The dictionary used for ArUco marker detection.
- `calibration_dictionary`: The dictionary used for camera calibration.
- `charuco_board`: The parameters used to construct the ChArUco board used for calibration.

Values read from NetworkTables can be accessed and adjusted through client interfaces. These parameters are:

- `camera_id`: The ID of the camera to be used.
- `camera_resolution_width`: The width of the camera resolution.
- `camera_resolution_height`: The height of the camera resolution.
- `camera_auto_exposure`: Whether the camera should use auto exposure or not.
- `camera_exposure`: The exposure of the camera.
- `camera_gain`: The gain of the camera.
- `camera_brightness`: The brightness of the camera.
- `fiducial_size`: The size of the ArUco markers in meters.
- `fiducial_layout`: The layout of the fiducial markers in the environment.

*Note that these values need to be updated in robot code to be saved as these values are not permanently stored locally.* 

Additional parameters accessible through the Config class are:

- `aruco_parameters`: The parameters used for ArUco marker detection.
- `camera_matrix`: The camera matrix values.
- `distortion_coefficients`: The camera distortion coefficients.

Values for the camera calibration parameters can be found in the `calibration.json` file.

Adjust these parameters according to your specific setup and requirements.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an [issue](https://github.com/anivanchen/aruco/issues) or submit a [pull request](https://github.com/anivanchen/aruco/pulls) on the project's GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to fork, use, and modify the code for your own purposes.
