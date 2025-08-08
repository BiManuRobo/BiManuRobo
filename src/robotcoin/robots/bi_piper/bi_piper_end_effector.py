from functools import cached_property
from typing import Any

from lerobot.errors import DeviceNotConnectedError
from lerobot.robots.robot import Robot

from .configuration_bi_piper import BiPiperEndEffectorConfig
from ..piper import PiperEndEffectorConfig
from ..piper import PiperEndEffector
from ...cameras import make_cameras_from_configs


class BiPiperEndEffector(Robot):
    """
    BiPiperEndEffector is a robot class for controlling the end effector of the BiPiper robot using end-effector control.

    Example:
        ```python
        config = BiPiperEndEffectorConfig(
            port_left="can1",
            port_right="can2",
            cameras={"front": {"type": "dummy_camera", "height": 480, "width": 640, "fps": 30}}
        )
        robot = BiPiperEndEffector(config)
        robot.connect()

        # get observation
        observation = robot.get_observation()

        # send action
        action = {
            "left_x": 0.1, "left_y": 0.2, "left_z": 0.3,
            "left_roll": 0.0, "left_pitch": 0.0, "left_yaw": 0.0, "left_gripper": 0.5,
            "right_x": 0.1, "right_y": 0.2, "right_z": 0.3,
            "right_roll": 0.0, "right_pitch": 0.0, "right_yaw": 0.0, "right_gripper": 0.5
        }
        robot.send_action(action)

        robot.disconnect()
        ```
    """
    
    config_class =  BiPiperEndEffectorConfig
    name = "bi_piper_end_effector"

    def __init__(self, config: BiPiperEndEffectorConfig):
        super().__init__(config)

        left_arm_config = PiperEndEffectorConfig(
            id=f"{config.id}_left" if config.id else None,
            port=config.port_left,
            cameras={},
            init_ee_state=config.init_ee_state,
        )
        right_arm_config = PiperEndEffectorConfig(
            id=f"{config.id}_right" if config.id else None,
            port=config.port_right,
            cameras={},
            init_ee_state=config.init_ee_state,
        )

        self.left_arm = PiperEndEffector(left_arm_config)
        self.right_arm = PiperEndEffector(right_arm_config)
        self.cameras = make_cameras_from_configs(config.cameras)
    
    @property
    def _motors_ft(self) -> dict[str, type]:
        return {
            {f"left_{each}": float for each in self.left_arm._motors_ft.keys()} |
            {f"right_{each}": float for each in self.right_arm._motors_ft.keys()}
        }
    
    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        cameras_features = {}
        for cam_name, cam in self.cameras.items():
            if hasattr(cam, 'observation_features'):
                features = cam.observation_features
                cameras_features.update({f"{cam_name}_{k}": v for k, v in features.items()})
            else:
                cameras_features[cam_name] = (cam.height, cam.width, 3)
        return cameras_features
    
    @cached_property
    def observation_features(self) -> dict:
        return {**self._motors_ft, **self._cameras_ft}
    
    @property
    def is_connected(self) -> bool:
        return self.left_arm.is_connected and self.right_arm.is_connected and all(cam.is_connected for cam in self.cameras.values())
    
    def connect(self):
        self.left_arm.connect()
        self.right_arm.connect()

        for cam in self.cameras.values():
            cam.connect()
    
    def is_calibrated(self) -> bool:
        return self.left_arm.is_calibrated and self.right_arm.is_calibrated
    
    def calibrate(self) -> None:
        self.left_arm.calibrate()
        self.right_arm.calibrate()
    
    def configure(self) -> None:
        self.left_arm.configure()
        self.right_arm.configure()
    
    def send_action(self, action: dict[str, Any]) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")
        
        left_action = {k.removeprefix("left_"): v for k, v in action.items() if k.startswith("left_")}
        right_action = {k.removeprefix("right_"): v for k, v in action.items() if k.startswith("right_")}

        send_action_left = self.left_arm.send_action(left_action)
        send_action_right = self.right_arm.send_action(right_action)

        send_action_left = {f"left_{k}": v for k, v in send_action_left.items()}
        send_action_right = {f"right_{k}": v for k, v in send_action_right.items()}
        return {**send_action_left, **send_action_right}
    
    def get_observation(self) -> dict[str, Any]:
        if not self.is_connected:
            raise DeviceNotConnectedError(f"{self} is not connected.")
        
        obs_dict = {}

        left_obs = self.left_arm.get_observation()
        obs_dict.update({f"left_{key}": value for key, value in left_obs.items()})

        right_obs = self.right_arm.get_observation()
        obs_dict.update({f"right_{key}": value for key, value in right_obs.items()})

        for cam_key, cam in self.cameras.items():
            outputs = cam.async_read()
            if isinstance(outputs, dict):
                for key, value in outputs.items():
                    obs_dict[f"{cam_key}.{key}"] = value
            else:
                obs_dict[cam_key] = outputs

        return obs_dict
    
    def disconnect(self):
        self.left_arm.disconnect()
        self.right_arm.disconnect()
        for cam in self.cameras.values():
            cam.disconnect()
        print("BiPiper robot disconnected.")
