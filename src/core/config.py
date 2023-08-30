import sys
from dotenv import dotenv_values
from loguru import logger

logger.remove(0)  # remove current default config
customized_config = {
    "colorize": True,
    "format": "<green>{time:YYYY-MM-D HH:mm:ss}</green> " +
    "<level>{level: <8}</level> | {message}",
    # "level": "INFO",
}
logger.add(sys.stderr, **customized_config)


class Config(object):

    @staticmethod
    def get(key: str) -> str:
        config = dotenv_values(".env")
        if key in config:
            return config[key]
        return ""
