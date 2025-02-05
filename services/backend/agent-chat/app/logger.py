import os
import logging


filepath = None if os.environ.get("DEBUG") \
                else os.environ.get("LOGGING_FILEPATH")

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(filename)s %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S,%f",
    filename=filepath
)

logger = logging.getLogger(__name__)
