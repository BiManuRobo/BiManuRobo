from enum import Enum
from pathlib import Path


class DatasetsHubEnum(str, Enum):
    HUGGINGFACE = "Huggingface"
    MODELSCOPE = "Modelscope"


DS_PLATFORM_NAME = "RobotCoin"

DEFAULT_UPLOAD_ALLOW_PATTERNS = []
DEFAULT_UPLOAD_IGNORE_PATTERNS = []

DEFAULT_DOWNLOAD_ALLOW_PATTERNS = []
DEFAULT_DOWNLOAD_IGNORE_PATTERNS = []

COMMIT_MESSAGE_FILE = Path(".commit_message")
COMMIT_MSG_LABEL = "commit_msg"
COMMIT_UUID_LABEL = "commit_uuid"

DATASETS_METAS_PATH = Path("datasets_meta/")

DATASETS_META_ALLOW_PATTERNS = [
    "meta/info.json",
    "meta/tasks.jsonl",
    "device/device_info.json",
    "label/annotation.json",
]

DATASETS_META_IGNORE_PATTERNS = []

MODELSCOPE_BUG_EXCEPTON_MSG = "Expecting value: line 1 column 1 (char 0)"

BIMANUROBO_DATASETS_INFO_FOLDER = ".bimanurobo_datasets_upload_infos/"

LEROBOT_META_FILE = "meta/info.json"
BIMANUROBO_DATASET_STRUCTURE = [
    COMMIT_MESSAGE_FILE,
    LEROBOT_META_FILE,
    "label/annotation.json",
    "label/task_tags.json",
]

BIMANUROBO_DATASETS_LOG_FOLDER = ".bimanurobo_datasets_upload_logs/"

DEFAULT_DOWNLOAD_PATH = f"~/.cache/{DS_PLATFORM_NAME}"
