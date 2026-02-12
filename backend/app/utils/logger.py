import logging
import os
from logging.handlers import RotatingFileHandler


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    FORMAT = "%(levelname)-8s | %(name)s | %(message)s"

    LEVEL_COLORS = {
        logging.DEBUG: Colors.BLUE + FORMAT + Colors.RESET,
        logging.INFO: Colors.GREEN + FORMAT + Colors.RESET,
        logging.WARNING: Colors.YELLOW + Colors.BOLD + FORMAT + Colors.RESET,
        logging.ERROR: Colors.RED + FORMAT + Colors.RESET,
        logging.CRITICAL: Colors.RED + Colors.BOLD + FORMAT + Colors.RESET,
    }

    def format(self, record):
        log_fmt = self.LEVEL_COLORS.get(record.levelno, self.FORMAT)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


root_logger = logging.getLogger()
root_logger.setLevel(logging.)

if not os.path.exists("logs"):
    os.makedirs("logs")

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

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

logger = logging.getLogger("OneFit")
