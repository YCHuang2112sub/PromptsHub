import logging
import sys
import os

# Global Debug Flag
DEBUG = True

def setup_diagnostics():
    """Configures the logging system."""
    if DEBUG:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - [%(name)s] [%(levelname)s] - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("logs/alphamind.log", encoding='utf-8')
            ]
        )
        logging.info("Diagnostics initialized and logging to console/file.")
    else:
        logging.disable(logging.CRITICAL)

def get_logger(name):
    """Returns a logger for a specific component."""
    return logging.getLogger(name)

def debug_log(message, level="info", name="AlphaMind"):
    """Legacy helper for simple string logging."""
    if not DEBUG:
        return
    logger = get_logger(name)
    if level == "info": logger.info(message)
    elif level == "debug": logger.debug(message)
    elif level == "error": logger.error(message)
    elif level == "warning": logger.warning(message)
