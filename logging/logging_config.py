import json, logging, logging.config, os, sys
from pythonjsonlogger import jsonlogger     # `pip install python-json-logger`

def setup_logging() -> None:
    env = os.getenv("ENV", "dev")

    log_level = "INFO" if env == "prod" else "DEBUG"
    handler_cfg = (
        {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        }
    )

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "simple": {"format": "%(levelname)s | %(name)s | %(message)s"},
                "json": {
                    "()": jsonlogger.JsonFormatter,
                    "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s",
                },
            },
            "handlers": {"stdout": handler_cfg},
            "root": {"handlers": ["stdout"], "level": log_level},
        }
    )
