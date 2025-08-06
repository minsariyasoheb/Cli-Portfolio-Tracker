import sys
import sqlite3
import logging
from app.config import LOG_FILE,DB_FILE,CSV_FILE

# Formatter setup
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%d/%m/%y %H:%M'
)

# File handler for writing logs
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)

# Main logger for app-wide use
main_logger = logging.getLogger("PortfolioTracker")
main_logger.setLevel(logging.DEBUG)
main_logger.addHandler(file_handler)

# Modular loggers for specific modules
loggers = {}
for name in ["AddStocks", "RemoveStocks", "Database"]:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    loggers[name] = logger

logger = loggers["Database"]

def get_connection():
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        logger.error(f"DB connection failed: {e}")
        return None

def create_table():
    conn = get_connection()
    if conn:
        try:
            conn.execute("""CREATE TABLE IF NOT EXISTS portfolio(
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL UNIQUE,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        )""")
            conn.commit()
        except sqlite3.Error as e:
                logger.error(f"Error creating table: {e}")
        finally:
            conn.close()

def insert_buy(symbol, quantity, price):
    create_table()
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO portfolio (symbol, quantity, price)
                VALUES (?, ?, ?)
            ''', (symbol, quantity, price))
            conn.commit()
            logger.info(f"Inserted: {quantity} of {symbol} at ₹{price}")
        except sqlite3.Error as e:
            logger.error(f"Error inserting buy: {e}")
        finally:
            conn.close()

def sell_stock(symbol, sell_qty, sell_price):
    pass


class PortfolioTracker():

    def menu(self):
        print()
        print("="*6+" Portfolio Tracker "+"="*6)
        print("1. Add Stocks")
        print("2. Remove Stocks")
        print("3. Check portfolio")
        print("0. Exit")
        print("="*31)
    
    def add_stocks(self):
        symbol = input("Enter Symbol Name\n-> ").upper()
        qty = int(input("How much did you buy?\n-> "))
        if qty == 0:
            print("invalid input")
            return
        price = float(input("What price did you buy?\n-> "))
        print(f"Bought {qty} shares of {symbol} at ₹{price} each.")
    
    def remove_stocks(self):
        symbol = input("Enter Symbol Name\n-> ").upper()
        qty = int(input("How much did you sell?\n-> "))
        if qty == 0:
            print("invalid input")
            return
        price = float(input("What price did you sell?\n-> "))
        old_price = 1.0
        print(f"Sold {qty} shares of {symbol} at ₹{price} each.")
        pnl = (price * qty) - (old_price * qty)
        if pnl < 0:
            print(f"Loss made: {pnl:.2f}")
        elif pnl == 0:
            print(f"Stocks were sold at par")
        elif pnl > 0:
            print(f"Profit made: {pnl:.2f}")


    def run(self):
        while True:
            self.menu()
            choice = int(input("Enter Your Choice: "))

            if choice == 0:
                print("GoodBye!")
                sys.exit()
            elif choice == 1:
                self.add_stocks()
            elif choice == 2:
                self.remove_stocks()

if __name__ == "__main__":
    app = PortfolioTracker()
    app.run()