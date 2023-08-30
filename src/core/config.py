import sys
from dotenv import dotenv_values
from loguru import logger


class Config(object):

    @staticmethod
    def get(key: str) -> str:
        config = dotenv_values(".env")
        if key in config:
            return config[key]
        return ""


debug_mode: bool = Config.get("ENVIRONMENT") and Config.get(
    "ENVIRONMENT").lower() in ["dev", "develop", "development"]
default_format: str = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> "
    "[<level>{level}</level>] "
    "<cyan><u>{name}</u></cyan> | "
    # "<cyan>{function}:{line}</cyan>| "
    "{message}"
)

logger.remove()  # remove current default config
logger.add(
    sys.stderr,
    level="DEBUG" if debug_mode else "INFO",
    diagnose=debug_mode,
    format=default_format,
)
