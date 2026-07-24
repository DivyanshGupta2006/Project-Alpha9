"""
[Title] - Main control centre

[Paragraph Description] -
Handles all the calls to different modules of the program.

[Requirements] -
    src/Alpha9/pipeline/main_pipeline.py
    src/Alpha9/utility/get_path.py
    src/Alpha9/utility/get_config.py

[Usages] -
    launch.py
"""

import logging
import sys
from datetime import datetime

from Alpha9.pipeline import main_pipeline
from Alpha9.utility import get_config, get_path


def set_logger() -> None:
    """
    [Paragraph Description] -
    Initializes and configures the root logger.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    config = get_config.load()
    path = get_path.absolute(config["path"]["log"])
    get_path.check(path)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(
                path / f"Alpha9_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log",
                encoding="utf-8",
            ),
            logging.StreamHandler(sys.stdout),
        ],
    )


def start() -> None:
    """
    [Paragraph Description] -
    Main entry point of the program.
    This manages all the calls to main scripts of each module.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    set_logger()
    logger = logging.getLogger("Alpha9")

    logger.info("Welcome to Alpha9!")

    choice = input("Update the data [y/n] : ")
    update = choice.lower() == "y"

    try:
        if update:
            choice = input("Force download the data [y/n] : ")
            force_download = choice.lower() == "y"
            success = main_pipeline.run(force_download)
            if success:
                logger.info("Alpha9 execution finished successfully.")
                logger.info("Thank you for using Alpha9!")
                sys.exit(0)
            else:
                logger.error(
                    "Alpha9 execution terminated due to an error in the pipeline."
                )
                sys.exit(1)

    except Exception as e:
        logger.exception(f"Alpha9 execution terminated due to unhandled error: {e}")
        sys.exit(1)
