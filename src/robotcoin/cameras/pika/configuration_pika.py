from dataclasses import dataclass

from lerobot.cameras.configs import CameraConfig


@CameraConfig.register_subclass("pika")
@dataclass
class PikaCameraConfig(CameraConfig):
    """
    Configuration class for the PikaCamera.
    
    Attributes:
        usb: USB device path for the camera.
        fisheye_camera_index: Index of the fisheye camera (if applicable).
        realsense_serial_number: Serial number of the realsense camera (if applicable).
        width: Width of the camera frames.
        height: Height of the camera frames.
        fps: Frames per second for the camera.
    """

    usb: str
    fisheye_camera_index: int | None = None
    realsense_serial_number: str | None = None

    def __post_init__(self):
        if self.fisheye_camera_index is None and self.realsense_serial_number is not None:
            raise ValueError("One of fisheye camera index or realsense serial number must be provided")
