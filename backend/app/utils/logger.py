import logging
import os
import time
from logging.handlers import RotatingFileHandler

from app import Config


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    LEVEL_FORMATS = {
        logging.DEBUG: f"{Colors.DIM}DEBUG   {Colors.RESET} | %(name)-20s | {Colors.DIM}%(message)s{Colors.RESET}",
        logging.INFO: f"{Colors.GREEN}INFO    {Colors.RESET} | %(name)-20s | %(message)s",
        logging.WARNING: f"{Colors.YELLOW}{Colors.BOLD}WARNING {Colors.RESET} | %(name)-20s | {Colors.YELLOW}%(message)s{Colors.RESET}",
        logging.ERROR: f"{Colors.RED}ERROR   {Colors.RESET} | %(name)-20s | {Colors.RED}%(message)s{Colors.RESET}",
        logging.CRITICAL: f"{Colors.RED}{Colors.BOLD}CRITICAL{Colors.RESET} | %(name)-20s | {Colors.RED}{Colors.BOLD}%(message)s{Colors.RESET}",
    }

    def format(self, record):
        log_fmt = self.LEVEL_FORMATS.get(record.levelno, "%(levelname)-8s | %(name)-20s | %(message)s")
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

if not root_logger.handlers:
    os.makedirs("logs", exist_ok=True)

    # Fichier
    file_handler = RotatingFileHandler(
        "logs/api.log",
        maxBytes=5 * 1024 * 1024,  # 5 Mo
        backupCount=5,  # Garde les 5 derniers fichiers
        encoding="utf-8",
    )

    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    file_handler.setLevel(getattr(logging, Config.LOG_LEVEL_FILE, logging.DEBUG))

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())
    console_handler.setLevel(getattr(logging, Config.LOG_LEVEL_CONSOLE, logging.INFO))

    # On rajoute
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


logging.getLogger("werkzeug").setLevel(getattr(logging, Config.LOG_LEVEL_WERKZEUG, logging.WARNING))
logging.getLogger("urllib3").setLevel(getattr(logging, Config.LOG_LEVEL_URLLIB3, logging.WARNING))
logging.getLogger("sqlalchemy.engine").setLevel(getattr(logging, Config.LOG_LEVEL_SQLALCHEMY, logging.WARNING))


logger = logging.getLogger("OneFit")
logger.setLevel(getattr(logging, Config.LOG_LEVEL_ONEFIT, logging.INFO))

auth_logger = logging.getLogger("OneFit.Auth")
auth_logger.setLevel(getattr(logging, Config.LOG_LEVEL_ONEFIT_AUTH, logging.INFO))

db_logger = logging.getLogger("OneFit.Database")
db_logger.setLevel(getattr(logging, Config.LOG_LEVEL_ONEFIT_DATABASE, logging.INFO))

api_logger = logging.getLogger("OneFit.ApiCache")
api_logger.setLevel(getattr(logging, Config.LOG_LEVEL_ONEFIT_APICACHE, logging.INFO))

perf_logger = logging.getLogger("OneFit.Performance")
perf_logger.setLevel(getattr(logging, Config.LOG_LEVEL_ONEFIT_PERFORMANCE, logging.INFO))

route_logger = logging.getLogger("OneFit.Routes")
route_logger.setLevel(getattr(logging, Config.LOG_LEVEL_ONEFIT_ROUTES, logging.INFO))


class QueryTimer:
    """Context manager pour mesurer et logger le temps de chaque Query"""

    def __init__(self, operation: str):
        self.operation = operation
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start) * 1000  # type: ignore
        if exc_type:
            db_logger.error(f"ERREUR QUERY | {self.operation} | {duration_ms:.1f}ms | {exc_type.__name__}: {exc_val}")
        else:
            db_logger.info(f"QUERY | {self.operation} | {duration_ms:.1f}ms")
        return False
