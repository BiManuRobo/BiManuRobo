"""
Bimanurobo Datasets Uploader
usage:
python -m bimanurobo.datasets.upload --config configs/upload.yaml
"""

from pathlib import Path
import logging
from datetime import datetime
import json
from tqdm import tqdm

from dataclasses import field

import draccus

from bimanurobo.datasets.constant import BIMANUROBO_DATASETS_INFO_FOLDER, DatasetsHubEnum
from bimanurobo.datasets.log_config import DatasetsLogConfig
from bimanurobo.datasets.constant import (
    BIMANUROBO_DATASET_STRUCTURE,
    COMMIT_MESSAGE_FILE,
    COMMIT_MSG_LABEL,
    COMMIT_UUID_LABEL,
    DS_PLATFORM_NAME,
)

from bimanurobo.datasets.hubs import HuggingfaceUploadHub, ModelscopeUploadHub


class DsUploadConfig:
    upload_root_path: Path = field(default_factory=Path)
    repo_list: list[str] = field(default_factory=list[str])
    upload_all: bool = True
    hub: DatasetsHubEnum = DatasetsHubEnum.HUGGINGFACE
    upload_ignore_dirs: list[str] = field(default_factory=list[str])
    hub_owner_name: str = ""
    token: str = ""
    upload_log: DatasetsLogConfig


class DsUploadUtil:
    def __init__(self, config: DsUploadConfig) -> None:
        self.config: DsUploadConfig = config
        self.logger = self._setup_logger()

        if config.hub == DatasetsHubEnum.MODELSCOPE:
            self.hub = ModelscopeUploadHub(self.config.token)
        elif config.hub == DatasetsHubEnum.HUGGINGFACE:
            self.hub = HuggingfaceUploadHub(self.config.token)
        else:
            raise Exception(f"hub {config.hub} is not supported.")
        pass

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"DsUploadUtil-{self.config.hub}")
        logger.setLevel(getattr(logging, self.config.upload_log.log_level.upper()))

        if logger.handlers:
            logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # ========== 动态生成带时间戳的日志文件名 ==========
        log_dir = Path(self.config.upload_log.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)  # 确保日志目录存在

        if self.config.upload_log.use_timestamp_in_logfile:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            log_filename = f"ds_upload_{timestamp}.log"
        else:
            log_filename = "ds_upload.log"  # 回退到固定名称

        log_filepath = log_dir / log_filename

        # ========== 添加文件处理器 ==========
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
        logger.info(f"日志已启用，输出到: {log_filepath}")

        return logger

    def _scan_dirs(self) -> list[Path]:
        root_abs_path: Path = self.config.upload_root_path.expanduser().absolute()
        err_msg = ""
        err: bool = False
        if not root_abs_path.exists():
            err = True
            err_msg = f"upload_root_path {root_abs_path} does not exists"

        if not root_abs_path.is_dir():
            err = True
            err_msg = f"{root_abs_path} is not a dir"

        if err:
            self.logger.error(err_msg)
            raise FileNotFoundError(err_msg)

        sub_dirs: list[Path] = [p for p in root_abs_path.iterdir() if p.is_dir()]
        return sub_dirs

    def _check_ds_valid(self, sub_dir: Path) -> bool:
        res = True
        for item in BIMANUROBO_DATASET_STRUCTURE:
            file_path = sub_dir.joinpath(item)
            if not file_path.exists():
                self.logger.info(
                    f"{sub_dir} is not a valid BiManuRobo dataset, due to less of file {file_path}"
                )
                res = False
        return res

    def _commit_msg_exists(self, sub_dir: Path) -> bool:
        return self.config.upload_root_path.joinpath(sub_dir).joinpath(COMMIT_MESSAGE_FILE).exists()

    def _get_commit_msg(self, sub_dir: Path) -> tuple[str, str]:
        commit_msg = ""
        commit_uuid = ""
        commit_msg_file_path = self.config.upload_root_path.joinpath(sub_dir).joinpath(
            COMMIT_MESSAGE_FILE
        )
        if self._commit_msg_exists(sub_dir):
            with open(commit_msg_file_path, encoding="utf-8") as f:
                data = json.load(f)
                commit_msg = data.get(COMMIT_MSG_LABEL)
                commit_uuid = data.get(COMMIT_UUID_LABEL)
        return commit_msg, commit_uuid

    def _get_commit_history_msg(self, sub_dir: Path) -> tuple[str, str]:
        commit_history_msg = ""
        commit_history_uuid = ""
        commit_msg_history_file_path = (
            self.config.upload_root_path.joinpath(BIMANUROBO_DATASETS_INFO_FOLDER)
            .joinpath(self.config.hub)
            .joinpath(sub_dir)
            .joinpath(".json")
        )
        if commit_msg_history_file_path.exists():
            with open(commit_msg_history_file_path, encoding="utf-8") as f:
                data = json.load(f)
                commit_history_msg = data.get(COMMIT_MSG_LABEL)
                commit_history_uuid = data.get(COMMIT_UUID_LABEL)

        return commit_history_msg, commit_history_uuid

    def _should_upload(self, sub_dir: Path) -> tuple[bool, str]:
        should_upload = True
        commit_msg, commit_uuid = self._get_commit_msg(sub_dir)
        _, commit_history_uuid = self._get_commit_history_msg(sub_dir)
        if commit_history_uuid == "":
            should_upload = True
        else:
            should_upload = commit_uuid == commit_history_uuid
        return should_upload, commit_msg

    def _upload_dataset(self, sub_dir: Path, commit_msg: str) -> bool:
        if not sub_dir.exists():
            raise FileNotFoundError(f"sub_dir {sub_dir} does not exist")

        repo_name = sub_dir.name
        repo_id = f"{DS_PLATFORM_NAME}/{repo_name}"

        if self.hub.repo_exists(repo_id=repo_id):
            self.logger.info(
                f"repo_id does not exists in f{self.config.hub}, uploading will create repo {repo_id}"
            )

        try:
            commit_url: str = self.hub.upload_repo(sub_dir, repo_id, commit_msg)
            self.logger.info(
                f"repo {repo_id} has been uploaded successfully, commit_url is: {commit_url}"
            )
        except Exception as e:
            self.logger.error(e)

        return False

    def upload_datasets(self) -> None:
        ds_num = 0
        update_ds_num = 0
        datasets_to_update: dict[Path, str] = field(default_factory=dict[Path, str])
        root_path = self.config.upload_root_path.expanduser().absolute()
        if root_path.exists():
            raise FileNotFoundError(
                f"upload root path {self.config.upload_root_path} does not exists"
            )

        for file in root_path.iterdir():
            if not file.is_dir():
                continue
            if self.config.upload_all:
                should_check = True
            else:
                should_check = file not in self.config.upload_ignore_dirs

            if should_check:
                ds_num += 1

            ds_path = root_path.joinpath(file)

            should_upload, commit_msg = self._should_upload(sub_dir=ds_path)
            if should_upload:
                datasets_to_update[ds_path] = commit_msg
                update_ds_num += 1
                self._upload_dataset(sub_dir=ds_path, commit_msg=commit_msg)

        self.logger.info(
            f"found {ds_num} in path {root_path}, {update_ds_num} datasets need to update."
        )

        for path, commit_msg in tqdm(
            datasets_to_update.items(), desc=f"upload {DS_PLATFORM_NAME} datasets"
        ):
            self._upload_dataset(sub_dir=path, commit_msg=commit_msg)

    pass


if __name__ == "__main__":
    config = draccus.parse(DsUploadConfig)
    pass
