import logging
from os import getenv
from multiprocessing import Queue
from logging_loki import LokiQueueHandler
from uvicorn import logging as uvicorn_logging

# Create a custom formatter for uvicorn.access logger
console_formatter = uvicorn_logging.ColourizedFormatter(
    "{asctime} {levelprefix} : {message}",
    style="{", use_colors=True
)

# Create LokiQueueHandler with the desired settings
loki_logs_handler = LokiQueueHandler(
    Queue(-1),
    url=getenv("LOKI_ENDPOINT"),
    tags={"application": "fastapi"},
    version="1",
)

# Get the uvicorn.access logger
uvicorn_access_logger = logging.getLogger("uvicorn.access")

# Add LokiQueueHandler to the logger
uvicorn_access_logger.addHandler(loki_logs_handler)

# Set the custom formatter for the first handler of the logger
if uvicorn_access_logger.handlers:
    uvicorn_access_logger.handlers[0].setFormatter(console_formatter)

# Function to add logs to Loki
def add_logs_loki(log_message, error=False):
    if error:
        uvicorn_access_logger.error(log_message)
    else:
        uvicorn_access_logger.info(log_message)
