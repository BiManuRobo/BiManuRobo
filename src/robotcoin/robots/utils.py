from lerobot.robots.robot import RobotConfig
from lerobot.robots.robot import Robot


def make_robot_from_config(config: RobotConfig) -> Robot:
    if config.type == "koch_follower":
        from lerobot.robots.koch_follower import KochFollower

        return KochFollower(config)
    elif config.type == "so100_follower":
        from lerobot.robots.so100_follower import SO100Follower

        return SO100Follower(config)
    elif config.type == "so100_follower_end_effector":
        from lerobot.robots.so100_follower import SO100FollowerEndEffector

        return SO100FollowerEndEffector(config)
    elif config.type == "so101_follower":
        from lerobot.robots.so101_follower import SO101Follower

        return SO101Follower(config)
    elif config.type == "lekiwi":
        from lerobot.robots.lekiwi import LeKiwi

        return LeKiwi(config)
    elif config.type == "stretch3":
        from lerobot.robots.stretch3 import Stretch3Robot

        return Stretch3Robot(config)
    elif config.type == "viperx":
        from lerobot.robots.viperx import ViperX

        return ViperX(config)
    elif config.type == "hope_jr_hand":
        from lerobot.robots.hope_jr import HopeJrHand

        return HopeJrHand(config)
    elif config.type == "hope_jr_arm":
        from lerobot.robots.hope_jr import HopeJrArm

        return HopeJrArm(config)
    elif config.type == "bi_so100_follower":
        from lerobot.robots.bi_so100_follower import BiSO100Follower

        return BiSO100Follower(config)
    elif config.type == "mock_robot":
        from lerobot.robots.ests.mock_robot import MockRobot

        return MockRobot(config)
    elif config.type == "dummy":
        from .dummy.dummy import DummyRobot

        return DummyRobot(config)
    elif config.type == "piper":
        from .piper.piper import Piper

        return Piper(config)
    elif config.type == "bi_piper":
        from .bi_piper.bi_piper import BiPiper

        return BiPiper(config)
    else:
        raise ValueError(config.type)