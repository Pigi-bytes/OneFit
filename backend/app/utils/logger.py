import logging
import os
import time
from logging.handlers import RotatingFileHandler

LOG_LEVEL_CONSOLE = os.environ.get("LOG_LEVEL_CONSOLE", "INFO").upper()
LOG_LEVEL_FILE = os.environ.get("LOG_LEVEL_FILE", "DEBUG").upper()

# Control logging of external libraries via ENV
LOG_SQLALCHEMY = os.environ.get("LOG_SQLALCHEMY", "0") == "1"
LOG_WERKZEUG = os.environ.get("LOG_WERKZEUG", "0") == "1"
LOG_URLLIB3 = os.environ.get("LOG_URLLIB3", "0") == "1"
LOG_DB_POOL = os.environ.get("LOG_DB_POOL", "0") == "1"


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
    file_handler.setLevel(logging.DEBUG)

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())
    console_handler.setLevel(logging.INFO)  # Pas de pollution de la console

    # On rajoute
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


logging.getLogger("werkzeug").setLevel(logging.DEBUG if LOG_WERKZEUG else logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.DEBUG if LOG_URLLIB3 else logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG if LOG_SQLALCHEMY else logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG if LOG_DB_POOL else logging.WARNING)


logger = logging.getLogger("OneFit")
auth_logger = logging.getLogger("OneFit.Auth")
db_logger = logging.getLogger("OneFit.Database")
api_logger = logging.getLogger("OneFit.ApiCache")
perf_logger = logging.getLogger("OneFit.Performance")
route_logger = logging.getLogger("OneFit.Routes")


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
