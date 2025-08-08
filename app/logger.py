import logging
from app.config import Config

class Logger:
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt='%d/%m/%y %H:%M'
    )

    # File handler
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)

    @staticmethod
    def create_logger( name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(Logger.file_handler)
        logger.propagate = False
        return logger

Logger.loggers = {
    "main": Logger.create_logger("PortfolioTracker"),
    "buy": Logger.create_logger("Buy Stocks"),
    "sell": Logger.create_logger("Sell Stocks"),
    "update": Logger.create_logger("Update Stocks"),
    "capital": Logger.create_logger("Capital"),
    "db": Logger.create_logger("Database"),
    "portfolio": Logger.create_logger("Portfolio"),
    "transact": Logger.create_logger("Transaction/CSV"),
    "api": Logger.create_logger("Api")
}