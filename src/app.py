from loguru import logger
from .core.handler import MetadataFileHandler


def main() -> None:
    mfh: object = MetadataFileHandler()
    if mfh.map_to_nfo():
        logger.info("Generating NFO formatted metadata file completed")
    return


if __name__ == "__main__":
    main()
