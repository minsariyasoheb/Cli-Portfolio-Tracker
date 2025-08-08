import logging
from app.config import Config

# Define formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%d/%m/%y %H:%M'
)

# File handler
file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)

class Logger:
    def create_logger(name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.propagate = False
        return logger

    # Core loggers
    loggers = {
        "main": create_logger("PortfolioTracker"),
        "buy": create_logger("Buy Stocks"),
        "sell": create_logger("Sell Stocks"),
        "update": create_logger("Update Stocks"),
        "capital": create_logger("Capital"),
        "db": create_logger("Database"),
        "portfolio": create_logger("Portfolio"),
        "transact": create_logger("Transaction/CSV"),
        "api": create_logger("Api")
    }