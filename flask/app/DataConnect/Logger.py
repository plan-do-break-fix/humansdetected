import logging
import watchtower

def cloudwatch_logger() -> logging.Logger:
    """
    Returns a Logger formatted to write logs to stdout only.
    Intended for use with awslogs log driver.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LeMartin")
    logger.addHandler(watchtower.CloudWatchLogHandler())
    return logger