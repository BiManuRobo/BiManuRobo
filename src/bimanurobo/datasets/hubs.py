from abc import ABC, abstractmethod
from pathlib import Path
import logging

from huggingface_hub import HfApi
from modelscope.hub.api import HubApi
from modelscope.models.base import logger

from bimanurobo.datasets.constant import (
    DEFAULT_DOWNLOAD_ALLOW_PATTERNS,
    DEFAULT_DOWNLOAD_IGNORE_PATTERNS,
    DEFAULT_UPLOAD_ALLOW_PATTERNS,
    DEFAULT_UPLOAD_IGNORE_PATTERNS,
    MODELSCOPE_BUG_EXCEPTON_MSG,
)


class AbstractUploadHub(ABC):
    def __init__(self, token: str) -> None:
        self.token = token

    def disable_hub_logger(self, logger: logging.Logger) -> None:
        logger.setLevel(logging.CRITICAL + 1)

    @abstractmethod
    def upload_repo(self, folder_path: Path, repo_id: str, commit_msg: str) -> str:
        pass

    @abstractmethod
    def repo_exists(self, repo_id: str) -> bool:
        pass


class ModelscopeUploadHub(AbstractUploadHub):
    from modelscope.hub.api import HubApi
    from modelscope.hub.api import logger

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.hub = HubApi()
        self.disable_hub_logger(logger)

    def repo_exists(self, repo_id: str) -> bool:
        return self.hub.repo_exists(repo_id=repo_id, token=self.token, repo_type="dataset")

    def upload_repo(self, folder_path: Path, repo_id: str, commit_msg: str) -> str:
        try:
            commit_info = self.hub.upload_folder(
                repo_id=repo_id,
                folder_path=folder_path,
                token=self.token,
                repo_type="dataset",
                allow_patterns=DEFAULT_UPLOAD_ALLOW_PATTERNS,
                ignore_patterns=DEFAULT_UPLOAD_IGNORE_PATTERNS,
                commit_message=commit_msg,
            )
        except Exception as e:
            if str(e) == MODELSCOPE_BUG_EXCEPTON_MSG:
                return f"Exception captured when Modelscope upload dataset {repo_id}, but the repo has been uploaded successfully."
            raise e

        return commit_info.commit_url


class HuggingfaceUploadHub(AbstractUploadHub):
    from huggingface_hub import HfApi
    from huggingface_hub.hf_api import logger

    logger_name = "hf_api"

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.hub = HfApi()
        self.disable_hub_logger(logger)

    def repo_exists(self, repo_id: str) -> bool:
        return self.hub.repo_exists(repo_id=repo_id, token=self.token, repo_type="dataset")

    def upload_repo(self, folder_path: Path, repo_id: str, commit_msg: str) -> str:
        commit_info = self.hub.upload_folder(
            repo_id=repo_id,
            folder_path=folder_path,
            token=self.token,
            repo_type="dataset",
            allow_patterns=DEFAULT_UPLOAD_ALLOW_PATTERNS,
            ignore_patterns=DEFAULT_UPLOAD_IGNORE_PATTERNS,
            commit_message=commit_msg,
        )
        return commit_info.commit_url


class AbstractDownloadHub(ABC):
    @abstractmethod
    def repo_exists(self, repo_id: str) -> bool:
        pass

    @abstractmethod
    def download_repo_with_patterns(
        self,
        repo_id: str,
        download_path: Path,
        allow_patterns: list[str] = DEFAULT_DOWNLOAD_ALLOW_PATTERNS,
        ignore_patterns: list[str] = DEFAULT_DOWNLOAD_IGNORE_PATTERNS,
    ) -> None:
        pass


class ModelscopeDownloadHub(AbstractDownloadHub):
    from modelscope.hub.api import HubApi

    hub = HubApi()

    def repo_exists(self, repo_id: str) -> bool:
        return self.hub.repo_exists(repo_id=repo_id, repo_type="dataset")

    def download_repo_with_patterns(
        self,
        repo_id: str,
        download_path: Path,
        allow_patterns: list[str] = DEFAULT_DOWNLOAD_ALLOW_PATTERNS,
        ignore_patterns: list[str] = DEFAULT_DOWNLOAD_IGNORE_PATTERNS,
    ) -> None:
        from modelscope.hub.snapshot_download import snapshot_download

        download_path = download_path.expanduser().absolute()

        try:
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(download_path),
                allow_patterns=allow_patterns,
                ignore_patterns=ignore_patterns,
                repo_type="dataset",
            )
        except Exception as e:
            raise e


class HuggingfaceDownloadHub(AbstractDownloadHub):
    from huggingface_hub import HfApi

    hub = HfApi()

    def repo_exists(self, repo_id: str) -> bool:
        return self.hub.repo_exists(repo_id=repo_id, repo_type="dataset")

    def download_repo_with_patterns(
        self,
        repo_id: str,
        download_path: Path,
        allow_patterns: list[str] = DEFAULT_DOWNLOAD_ALLOW_PATTERNS,
        ignore_patterns: list[str] = DEFAULT_DOWNLOAD_IGNORE_PATTERNS,
    ) -> None:
        download_path = download_path.expanduser().absolute()
        try:
            self.hub.snapshot_download(
                repo_id=repo_id,
                local_dir=download_path,
                allow_patterns=allow_patterns,
                ignore_patterns=ignore_patterns,
                repo_type="dataset",
                token=False,
            )

        except Exception as e:
            raise e
