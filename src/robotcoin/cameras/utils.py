from pathlib import Path
from typing import TypeAlias

from lerobot.cameras.camera import Camera
from lerobot.cameras.configs import CameraConfig


IndexOrPath: TypeAlias = int | Path


def make_cameras_from_configs(camera_configs: dict[str, CameraConfig]) -> dict[str, Camera]:
    cameras = {}

    for key, cfg in camera_configs.items():
        if cfg.type == "opencv":
            from lerobot.cameras.opencv import OpenCVCamera

            cameras[key] = OpenCVCamera(cfg)

        elif cfg.type == "intelrealsense":
            from lerobot.cameras.realsense.camera_realsense import RealSenseCamera

            cameras[key] = RealSenseCamera(cfg)
        
        elif cfg.type == "dummy":
            from .dummy import DummyCamera

            cameras[key] = DummyCamera(cfg)
        
        elif cfg.type == "pika":
            from .pika import PikaCamera

            cameras[key] = PikaCamera(cfg)
        else:
            raise ValueError(f"The motor type '{cfg.type}' is not valid.")

    return cameras