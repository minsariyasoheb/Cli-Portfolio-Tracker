import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")
    DB_FILE = os.path.join(DATA_DIR, "portfolio.db")
    CSV_FILE = os.path.join(DATA_DIR, "transactions.csv")
    LOG_FILE = os.path.join(DATA_DIR, "portfolio_tracker.log")