import logging
import colorlog

from sbtb.core.config import settings

LOGGER_NAME = "sbtb"


class CustomLogger(logging.Logger):
    _instance = None

    def __init__(self, name=LOGGER_NAME, log_level=settings.LOG_LEVEL) -> None:
        super().__init__(name, log_level)
        if not self.handlers:
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(levelname)s - [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] - %(filename)s:%(funcName)s:%(lineno)s - %(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
            )

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.addHandler(stream_handler)

    @classmethod
    def get_instance(cls, name: str = LOGGER_NAME, log_level: int = logging.INFO) -> 'CustomLogger':
        if cls._instance is None:
            cls._instance = cls(name, log_level)
        return cls._instance


logger: CustomLogger = CustomLogger.get_instance()