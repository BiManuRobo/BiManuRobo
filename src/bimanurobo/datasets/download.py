"""
# Bimanurobo Datasets Downloader
# usage:

# you can download datasets by specifing datasets names, which can ge searched at https://robotcoin.github.io/search.index
# the default download hub is huggingface
python -m bimanurobo.Datasets.download  --ds_names "aaa, bbb, ccc"

# you can also download datasets from modelscope
python -m bimanurobo.Datasets.download  --ds_names "aaa, bbb, ccc" --hub modelscope

# the default download saving path is ~/.cache/RobotCoin/huggingface/, or you can specify your download path
python -m bimanurobo.Datasets.download  --ds_names "aaa, bbb, ccc" --root_path ./datas/

# for more config info, please refer to ./configs/download.yaml
python -m bimanurobo.datasets.download --config configs/download.yaml

"""

from pathlib import Path
import logging
from datetime import datetime
from tqdm import tqdm
import re

from dataclasses import dataclass, field

import draccus

from bimanurobo.datasets.constant import (
    DS_PLATFORM_NAME,
    DatasetsHubEnum,
    DEFAULT_DOWNLOAD_PATH,
)
from bimanurobo.datasets.hubs import HuggingfaceDownloadHub, ModelscopeDownloadHub
from bimanurobo.datasets.log_config import DatasetsLogConfig


@dataclass
class DsDownloadConfig:
    upload_log: DatasetsLogConfig
    hub: DatasetsHubEnum = DatasetsHubEnum.HUGGINGFACE
    root_path: Path = Path(f"{DEFAULT_DOWNLOAD_PATH}/{hub}")
    ds_names: str = field(default_factory=str)


class DsDownloadUtil:
    def __init__(self, config: DsDownloadConfig) -> None:
        self.config: DsDownloadConfig = config
        self.logger = self._setup_logger()

        if config.hub == DatasetsHubEnum.MODELSCOPE:
            self.hub = ModelscopeDownloadHub()
        elif config.hub == DatasetsHubEnum.HUGGINGFACE:
            self.hub = HuggingfaceDownloadHub()
        else:
            raise Exception(f"hub {config.hub} is not supported.")
        pass

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"DsDownloadUtil-{self.config.hub}")
        logger.setLevel(getattr(logging, self.config.upload_log.log_level.upper()))

        if logger.handlers:
            logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        log_dir = self.config.root_path.joinpath(self.config.upload_log.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)  # 确保日志目录存在

        if self.config.upload_log.use_timestamp_in_logfile:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_filename = f"ds_download_{timestamp}.log"
        else:
            log_filename = "ds_download.log"

        log_filepath = log_dir / log_filename

        if self.config.upload_log.log_to_console:
            ch = logging.StreamHandler()
            ch.setLevel(getattr(logging, self.config.upload_log.log_level.upper()))
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        # 添加文件处理器
        fh = logging.FileHandler(log_filepath, encoding="utf-8")
        fh.setLevel(getattr(logging, self.config.upload_log.log_level.upper()))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        # 可选：记录日志文件路径
        logger.info(f"Logging enabled, output to: {log_filepath}")

        return logger

    def _get_dsname_list(self) -> list[str]:
        return [item for item in re.split(r"[,\s]+", self.config.ds_names.strip()) if item]

    def download_datasets(self) -> None:
        root_path = self.config.root_path.expanduser().absolute()
        if not root_path.exists():
            self.logger.info(f"download root path {root_path} does not exists, try to create it.")
            try:
                root_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.info(f"failed to mkdir {root_path}: {e}")

        ds_list = self._get_dsname_list()
        for ds_name in tqdm(ds_list, desc=f"download {DS_PLATFORM_NAME} datasets"):
            repo_id = f"{DS_PLATFORM_NAME}/{ds_name}"
            if not self.hub.repo_exists(repo_id):
                self.logger.warning(
                    f"repo {repo_id} does not exists in {self.config.hub} hub, please check error"
                )
                continue

            download_path = Path(f"{self.config.root_path}/{ds_name}")
            try:
                self.hub.download_repo_with_patterns(repo_id=repo_id, download_path=download_path)
            except Exception as e:
                self.logger.info(f"dataset {ds_name} download failed: {e}")


if __name__ == "__main__":
    config = draccus.parse(DsDownloadConfig)
    pass
