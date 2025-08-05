from dataclasses import dataclass


@dataclass()
class DatasetsLogConfig:
    log_level: str = "INFO"
    log_dir: str = "log"
    log_to_console: bool = True
    use_timestamp_in_logfile: bool = True
