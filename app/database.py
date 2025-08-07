import sqlite3
import os
import random
from app.config import Config

class Database:
    def get_db_connection(self):
        os.makedirs(os.path.dirname(Config.DB_FILE), exist_ok=True)
        conn = sqlite3.connect(Config.DB_FILE)
        return conn

    def create_table(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                qty INTEGER NOT NULL,
                avg_price REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def insert_stocks(self,symbol, qty, price):
        conn = self.get_db_connection()
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO portfolio (symbol, qty, avg_price) VALUES (?, ?, ?)", 
                (symbol, qty, price)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

    def update_stocks(self,symbol, qty, price):
        conn = self.get_db_connection()
        c = conn.cursor()
        try:
            c.execute(
                """
                UPDATE portfolio
                SET qty = ?, avg_price = ?
                WHERE symbol = ?
                """,
                (qty, price, symbol)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

    def check_symbol(self, symbol):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT qty, avg_price FROM portfolio WHERE symbol = ?", (symbol.upper(),))
        result = c.fetchone()
        conn.close()

        if result:
            qty, avg_price = result
            return True, qty, avg_price
        else:
            return False
        
    def view_portfolio(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT symbol, qty, avg_price FROM portfolio")
        result = c.fetchall()
        conn.close()

        if not result:
            print("Your portfolio is empty.")
            return

        print(f"\n{'Symbol':<10}{'Quantity':>10}{'Avg Price (₹)':>18}{'Curr Price (₹)':>18}{'P/L (₹)':>15}")
        print("-" * 75)

        total_pnl = 0

        for symbol, qty, avg_price in result:
            curr_price = random.uniform(10, 20)
            stock_pnl = (curr_price - avg_price) * qty
            total_pnl += stock_pnl

            print(f"{symbol:<10}{qty:>10}{avg_price:>18.2f}{curr_price:>18.2f}{stock_pnl:>15.2f}")

        print("=" * 75)
        print(f"{'Total P/L:':>56}{total_pnl:>15.2f}")
        print("-" * 75)

    def total_invested(self):
        conn = self.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT qty, avg_price FROM portfolio")
        rows = c.fetchall()
        conn.close()

        total = sum(qty * avg_price for qty, avg_price in rows)
        return total