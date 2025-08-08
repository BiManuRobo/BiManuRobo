import logging
import numpy as np
import time
from threading import Thread, Event, Lock
from typing import Any

from lerobot.cameras.camera import Camera
from lerobot.errors import DeviceAlreadyConnectedError, DeviceNotConnectedError

from pika import sense

from .configuration_pika import PikaCameraConfig


logger = logging.getLogger(__name__)


class PikaCamera(Camera):
    """
    PikaCamera implementation for Agilex Pika cameras.
    This camera supports both fisheye and realsense cameras, allowing for
    simultaneous capture of color and depth frames.
    This class is based on the Pika SDK, seeing https://github.com/agilexrobotics/pika_sdk

    Example:
        ```python
        config = PikaCameraConfig(
            usb=/dev/ttyUSB0,
            fisheye_camera_index=0,
            realsense_serial_number="1234567890",
            fps=30, width=640, height=480,
        )
        camera = PikaCamera(config)
        camera.connect()

        # outputs: dict with keys 'fisheye', 'realsense', and 'depth'
        # where 'fisheye' and 'realsense' are np.ndarrays of shape (height, width, 3)
        # and 'depth' is a np.ndarray of shape (height, width)
        outputs = camera.read()

        frame = camera.read()
        camera.disconnect()
    """

    def __init__(self, config: PikaCameraConfig):
        super().__init__(config)
        self.thread: Thread | None = None
        self.stop_event: Event | None = None
        self.frame_lock: Lock = Lock()
        self.latest_frame = None
        self.new_frame_event: Event = Event()

        self.usb = config.usb
        self.fisheye_camera_index = config.fisheye_camera_index
        self.realsense_serial_number = config.realsense_serial_number
        self.sense = sense(self.usb)

    @property
    def is_connected(self) -> bool:
        return self.sense.is_connected
    
    @property
    def observation_features(self) -> dict[str, tuple]:
        cameras = {}
        if self.fisheye_camera_index is not None:
            cameras['fisheye'] = (self.height, self.width, 3)
        if self.realsense_serial_number is not None:
            cameras['realsense'] = (self.height, self.width, 3)
            cameras['depth'] = (self.height, self.width)
        return cameras

    def connect(self) -> None:
        while not self.sense.connect():
            print("Waiting for Pika camera to connect...")
            time.sleep(0.1)

        self.sense.set_camera_param(self.width, self.height, self.fps)

        if self.fisheye_camera_index is not None:
            self.sense.set_fisheye_camera_index(self.fisheye_camera_index)
            self.fisheye_camera = self.sense.get_fisheye_camera()

        if self.realsense_serial_number is not None:
            self.sense.set_realsense_serial_number(self.realsense_serial_number)
            self.realsense_camera = self.sense.get_realsense_camera()

    @staticmethod
    def find_cameras() -> list[dict[str, Any]]:
        raise NotImplementedError("PikaCamera does not support method find_cameras")

    def read(self) -> np.ndarray:
        outputs = {}

        if self.fisheye_camera_index is not None:
            success, frame = self.fisheye_camera.get_frame()
            if not success:
                raise RuntimeError("Failed to get fisheye frame")
            outputs['fisheye'] = frame[:, :, ::-1]
        
        if self.realsense_serial_number is not None:
            success, color_frame = self.realsense_camera.get_color_frame()
            if not success:
                raise RuntimeError("Failed to get realsense color frame")
            outputs['realsense'] = color_frame[:, :, ::-1]
            
            success, depth_frame = self.realsense_camera.get_depth_frame()
            if not success:
                raise RuntimeError("Failed to get realsense depth frame")
            outputs['depth'] = depth_frame
        
        return outputs

    def _read_loop(self):
        while not self.stop_event.is_set():
            try:
                outputs = self.read()

                with self.frame_lock:
                    self.latest_frame = outputs
                self.new_frame_event.set()

            except DeviceNotConnectedError:
                break
            except Exception as e:
                logger.warning(f"Error reading frame in background thread for {self}: {e}")

    def _start_read_thread(self) -> None:
        """Starts or restarts the background read thread if it's not running."""
        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=0.1)
        if self.stop_event is not None:
            self.stop_event.set()

        self.stop_event = Event()
        self.thread = Thread(target=self._read_loop, args=(), name=f"{self}_read_loop")
        self.thread.daemon = True
        self.thread.start()

    def _stop_read_thread(self) -> None:
        """Signals the background read thread to stop and waits for it to join."""
        if self.stop_event is not None:
            self.stop_event.set()

        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        self.thread = None
        self.stop_event = None

    def async_read(self, timeout_ms: float = 200) -> np.ndarray:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")

        if self.thread is None or not self.thread.is_alive():
            self._start_read_thread()

        if not self.new_frame_event.wait(timeout=timeout_ms / 1000.0):
            thread_alive = self.thread is not None and self.thread.is_alive()
            raise TimeoutError(
                f"Timed out waiting for frame from camera {self} after {timeout_ms} ms. "
                f"Read thread alive: {thread_alive}."
            )

        with self.frame_lock:
            frame = self.latest_frame
            self.new_frame_event.clear()

        if frame is None:
            raise RuntimeError(f"Internal error: Event set but no frame available for {self}.")

        return frame

    def disconnect(self) -> None:
        self.sense.disconnect()
