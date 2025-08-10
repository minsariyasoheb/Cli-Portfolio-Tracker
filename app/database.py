import sqlite3
import os
import random
from app.config import Config
from app.logger import Logger
from app.transact import Transactions
from tabulate import tabulate

class Database:
    def __init__(self):
        self.logger = Logger.loggers["db"]
        self.create_table()
        self.transact = Transactions()
        

    def get_db_connection(self):
        os.makedirs(os.path.dirname(Config.DB_FILE), exist_ok=True)
        conn = sqlite3.connect(Config.DB_FILE)
        self.logger.debug("Opened database connection.")
        return conn

    def create_table(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        try:
            c.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL UNIQUE,
                    qty INTEGER NOT NULL,
                    avg_price REAL NOT NULL
                )
            """)
            self.logger.info("Checked/created portfolio table.")
            conn.commit()
        except Exception as e:
            self.logger.exception("Failed to create portfolio table.")
        finally:
            conn.close()
            
    def get_capital(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        try:
            c.execute("""
                CREATE TABLE IF NOT EXISTS capital (
                    id INTEGER PRIMARY KEY,
                    amount REAL NOT NULL
                )
            """)
            c.execute("SELECT COUNT(*) FROM capital")
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO capital (id, amount) VALUES (1, 0.0)")
                conn.commit()
                self.logger.info("Initialized capital with ₹0.00")

            c.execute("SELECT amount FROM capital WHERE id = 1")
            capital = c.fetchone()[0]
            self.logger.debug(f"Fetched capital: ₹{capital:.2f}")
            return capital
        except Exception as e:
            self.logger.exception("Error fetching capital.")
            return 0.0
        finally:
            conn.close()

    def update_capital(self, amount):
        try:
            conn = self.get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE capital SET amount = ? WHERE id = 1", (amount,))
            conn.commit()
            self.logger.info(f"Updated capital to ₹{amount:.2f}")
        except Exception as e:
            self.logger.exception("Failed to update capital.")
        finally:
            conn.close()

    def set_capital(self):
        logger = Logger.loggers["capital"]

        try:
            current = self.get_capital()
            capital = self.get_capital()
            table = [["Current Capital", f"₹{capital}"]]
            print(tabulate(table, tablefmt="fancy_grid"))
            logger.info(f"Fetched current capital: ₹{current:.2f}")

            new_amount = float(input("Enter your capital amount:\n-> "))

            if new_amount < 0:
                print("Capital cannot be negative.")
                logger.warning("Attempted to set negative capital.")
                return

            self.update_capital(new_amount)

            headers = ["Old Capital","New Capital"]
            table = [[f"₹{current:.2f}", f"₹{new_amount:.2f}"]]
            print(tabulate(table, headers=headers,tablefmt="fancy_grid"))

            logger.info(f"Capital updated to ₹{new_amount:.2f}")
            transact_log = Logger.loggers["transact"]
            self.transact.capital_transact("update",new_amount,current)
            transact_log.info("Updated Capital")

        except ValueError:
            print("Invalid input. Please enter a valid number.")
            logger.error("Invalid input while setting capital (not a float).")

    def add_capital(self):
        logger = Logger.loggers["capital"]

        current = self.get_capital()
        logger.info(f"Fetched current capital: ₹{current:.2f}")

        try:
            add_amount = float(input("Enter additional amount:\n-> "))

            if add_amount < 0:
                print("Additional amount cannot be negative.")
                logger.warning(f"Attempted to add negative capital: ₹{add_amount:.2f}")
                return

            new_amount = current + add_amount
            self.update_capital(new_amount)

            headers = ["Old Capital", "Add Capital", "New Capital"]
            table = [[f"₹{current:.2f}", f"₹{add_amount:.2f}", f"₹{new_amount:.2f}"]]
            print(tabulate(table, headers=headers,tablefmt="fancy_grid"))

            logger.info(f"Capital increased by ₹{add_amount:.2f}, new total: ₹{new_amount:.2f}")
            transact_log = Logger.loggers["transact"]
            self.transact.capital_transact("update",new_amount,current)
            transact_log.info("Updated Capital")

        except ValueError:
            print("Invalid input. Please enter a valid number.")
            logger.error("Invalid input for add_capital (non-numeric).")

    def withdraw_capital(self):
        logger = Logger.loggers["capital"]

        current = self.get_capital()
        logger.info(f"Fetched current capital: ₹{current:.2f}")

        try:
            withdraw_amount = float(input("Enter your capital amount:\n-> "))

            if withdraw_amount < 0:
                print("Amount cannot be negative.")
                logger.warning(f"Attempted to withdraw negative amount: ₹{withdraw_amount:.2f}")
                return

            if withdraw_amount > current:
                print("Insufficient capital.")
                logger.warning(f"Attempted to withdraw ₹{withdraw_amount:.2f} but only ₹{current:.2f} available.")
                return

            new_amount = current - withdraw_amount
            logger.info(f"Withdrew ₹{withdraw_amount:.2f}, new capital: ₹{new_amount:.2f}")
            self.update_capital(new_amount)
            transact_log = Logger.loggers["transact"]
            self.transact.capital_transact("update",new_amount,current)
            transact_log.info("Updated Capital")


            headers = ["Old Capital", "Withdrawn Capital", "New Capital"]
            table = [[f"₹{current:.2f}", f"₹{withdraw_amount:.2f}", f"₹{new_amount:.2f}"]]
            print(tabulate(table, headers=headers,tablefmt="fancy_grid"))

        except ValueError:
            print("Invalid input. Please enter a valid number.")
            logger.error("Invalid input for withdraw_capital (non-numeric).")

    def insert_stocks(self, symbol, qty, price):
        logger = Logger.loggers["main"]
        conn = self.get_db_connection()
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO portfolio (symbol, qty, avg_price) VALUES (?, ?, ?)", 
                (symbol.upper(), qty, price)
            )
            conn.commit()
            logger.info(f"Inserted new stock: {symbol.upper()}, Quantity: {qty}, Avg Price: ₹{price:.2f}")
        except sqlite3.IntegrityError:
            logger.warning(f"Attempted to insert duplicate stock: {symbol.upper()}")
            print(f"{symbol.upper()} already exists in your portfolio.")
        except sqlite3.Error as e:
            logger.error(f"SQLite error on insert: {e}")
            print("Database error occurred while inserting stock.")
        finally:
            conn.close()

    def update_stocks(self, symbol, qty, price):
        logger = Logger.loggers["main"]
        conn = self.get_db_connection()
        c = conn.cursor()

        try:
            # Check if the symbol exists first
            c.execute("SELECT COUNT(*) FROM portfolio WHERE symbol = ?", (symbol.upper(),))
            if c.fetchone()[0] == 0:
                logger.warning(f"Tried to update non-existing stock: {symbol.upper()}")
                print(f"No stock with symbol {symbol.upper()} found.")
                return

            c.execute(
                """
                UPDATE portfolio
                SET qty = ?, avg_price = ?
                WHERE symbol = ?
                """,
                (qty, price, symbol.upper())
            )
            conn.commit()
            logger.info(f"Updated stock: {symbol.upper()} -> Quantity: {qty}, Avg Price: ₹{price:.2f}")
        except sqlite3.Error as e:
            logger.error(f"SQLite error during stock update: {e}")
            print("Database error occurred while updating stock.")
        finally:
            conn.close()

    def delete_stock(self, symbol):
        logger = Logger.loggers["main"]
        conn = self.get_db_connection()
        c = conn.cursor()

        try:
            # Check if the stock exists before deleting
            c.execute("SELECT COUNT(*) FROM portfolio WHERE symbol = ?", (symbol.upper(),))
            if c.fetchone()[0] == 0:
                logger.warning(f"Attempted to delete non-existing stock: {symbol.upper()}")
                print(f"Stock {symbol.upper()} not found in portfolio.")
                return

            c.execute("DELETE FROM portfolio WHERE symbol = ?", (symbol.upper(),))
            conn.commit()
            logger.info(f"Deleted stock: {symbol.upper()}")
        except sqlite3.Error as e:
            logger.error(f"SQLite error during stock deletion: {e}")
            print("Database error occurred while deleting stock.")
        finally:
            conn.close()

    def check_symbol(self, symbol):
        logger = Logger.loggers["main"]
        conn = self.get_db_connection()
        c = conn.cursor()
        symbol = symbol.upper()

        try:
            c.execute("SELECT qty, avg_price FROM portfolio WHERE symbol = ?", (symbol,))
            result = c.fetchone()
            if result:
                qty, avg_price = result
                logger.info(f"Symbol found: {symbol} (Qty: {qty}, Avg Price: ₹{avg_price:.2f})")
                return True, qty, avg_price
            else:
                logger.warning(f"Symbol not found in portfolio: {symbol}")
                return False
        except sqlite3.Error as e:
            logger.error(f"SQLite error while checking symbol {symbol}: {e}")
            print("Error occurred while checking symbol.")
            return False
        finally:
            conn.close()
  
    def view_portfolio(self):
        logger = Logger.loggers["main"]
        conn = self.get_db_connection()
        c = conn.cursor()

        try:
            c.execute("SELECT symbol, qty, avg_price FROM portfolio")
            result = c.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error fetching portfolio: {e}")
            print("Could not retrieve portfolio.")
            return
        finally:
            conn.close()

        if not result:
            logger.info("Portfolio is empty.")
            print("Your portfolio is empty.")
            return "empty"

        table_data = []
        total_pnl = 0

        for symbol, qty, avg_price in result:
            # Simulated price (replace with API call)
            curr_price = random.uniform(avg_price - (avg_price * 0.05), avg_price + (avg_price * 0.05))
            stock_pnl = (curr_price - avg_price) * qty
            total_pnl += stock_pnl

            table_data.append([
                symbol,
                qty,
                f"{avg_price:.2f}",
                f"{curr_price:.2f}",
                f"{stock_pnl:.2f}"
            ])

        # Add total row
        table_data.append(["TOTAL", "", "", "", f"{total_pnl:.2f}"])

        headers = ["Symbol", "Quantity", "Avg Price (₹)", "Curr Price (₹)", "P/L (₹)"]
        table_str = tabulate(table_data, headers=headers, tablefmt="fancy_grid")

        # Find width of the table from the first line
        table_width = len(table_str.split("\n")[0])

        # Create merged header box
        top_border = "╒" + "═" * (table_width - 2) + "╕"
        title = "PORTFOLIO".center(table_width - 2)
        title_line = f"│{title}│"

        # Print final output
        print(top_border)
        print(title_line)
        print(table_str)

        logger.info(f"Total portfolio P/L: ₹{total_pnl:.2f}")

    def total_invested(self):
        logger = Logger.loggers["main"]  # Use appropriate logger name
        conn = self.get_db_connection()
        c = conn.cursor()

        try:
            c.execute("SELECT qty, avg_price FROM portfolio")
            rows = c.fetchall()
            total = sum(qty * avg_price for qty, avg_price in rows)
            logger.debug(f"Total invested capital calculated: ₹{total:.2f}")
            return total

        except sqlite3.Error as e:
            logger.error(f"Database error during total_invested(): {e}")
            return 0

        finally:
            conn.close()