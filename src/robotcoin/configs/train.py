from dataclasses import dataclass

from lerobot.configs.train import TrainPipelineConfig as TrainPipelineConfig_


@dataclass
class TrainPipelineConfig(TrainPipelineConfig_):
    """
    Configuration class for the training pipeline, extends the lerobot TrainPipelineConfig

    Attributes:
        input_keys: List of keys of input features to be used for the policy.
    """
    
    input_keys: list[str] = None
