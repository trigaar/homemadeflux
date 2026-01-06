import logging
import os
from pathlib import Path


def setup_logging(log_dir: str | os.PathLike = "logs") -> logging.Logger:
    """
    Configure application-wide logging.

    Args:
        log_dir: Directory where log files should be stored.

    Returns:
        Configured root logger.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    log_file = log_path / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger("home_made_flux")
    logger.debug("Logging initialized at %s", log_file)
    return logger
