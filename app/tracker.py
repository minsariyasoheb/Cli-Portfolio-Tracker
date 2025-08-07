import random
import sys
import os
import logging
from app.database import Database
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class PortfolioTracker():

    def __init__(self):
        self.transactions = []
        self.portfolio = {}
        self.capital = 0.0

    def main_menu(self):
        print("\n1. Capital Menu")
        print("2. Stocks Menu")
        print("3. View Transactions")
        print("4. View Portfolio")
        print("0. Exit")

    def stocks_menu(self):
        clear_screen()
        print("1. Buy Stocks")
        print("2. Sell Stocks")
        print("3. Update Stock Details")
        print("0. Return to Main Menu")
        
    def buy_stocks(self):
        db = Database()
        db.create_table()
        capital = db.get_capital()

        symbol = input("Enter symbol name\n-> ").upper()
        try:
            qty = int(input("How many did you buy?\n-> "))
            if qty <=0:
                print("Error: Buying quantity cannot be 0 or less than 0")
                return
            price = float(input("How much was each stock?\n-> "))
            if price <=0:
                print("Error: Buying price cannot be 0 or less than 0")
                return
            elif price > capital:
                print("Error: You do not have enough capital to buy this stock")
                return
            now = datetime.now().strftime("%d/%m/%y %H:%M")
            remaining_capital = capital - price
            db.update_capital(remaining_capital)
            result = db.check_symbol(symbol)
            if result is False:
                db.insert_stocks(symbol, qty, price)
            else:
                # Symbol already exists, update quantity and average price
                exists, old_qty, old_price = result
                del exists
                new_qty = old_qty + qty
                new_avg_price = ((old_qty * old_price) + (qty * price)) / new_qty
                new_avg_price = round(new_avg_price, 2)

                # Update in DB
                db.update_stocks(symbol, new_qty, new_avg_price)

        except Exception as e:
            print("Error:", e)
        
    def sell_stocks(self):
        db = Database()
        db.create_table()

        symbol = input("Enter symbol name\n-> ").upper()
        result = db.check_symbol(symbol)
        if result is False:
            print("Error: Symbol does not exist")
            return
        else:
            exists, qty, price = result
            del exists
            try:
                sold_qty = int(input("How many did you sell?\n-> "))
                if sold_qty > qty:
                    print("Error: Selling quantity cannot exceed existing quantity")
                    return
                price = float(input("How much was each stock?\n-> "))
                qty -= sold_qty
                amount = db.get_capital()
                new_amount = amount + (price*sold_qty)
                db.update_capital(new_amount)
                
            except Exception as e:
                print("Error:", e)

    def update_stocks(self):
        db = Database()
        db.create_table()

        try:
            clear_screen()
            print("1. Add Multiple Stocks")
            print("2. Update All Stocks")
            print("0. Exit")
            choice = int(input("\n-> "))

            if choice == 0:
                return

            elif choice == 1:
                num = int(input("How many stocks do you want to add?\n-> "))
                for i in range(1, num + 1):  # Fix: use `num + 1` to include last one
                    print(f"\nStock #{i}")
                    symbol = input("Enter symbol name\n-> ").upper()
                    qty = int(input("How many did you buy?\n-> "))
                    if qty <= 0:
                        print("Error: Quantity must be > 0.")
                        return
                    price = float(input("What was the price per stock?\n-> "))
                    if price <= 0:
                        print("Error: Price must be > 0.")
                        return
                    db.insert_stocks(symbol, qty, price)

            elif choice == 2:
                clear_screen()
                print("Your current portfolio:")
                db.view_portfolio()

                conn = db.get_db_connection()
                c = conn.cursor()
                c.execute("SELECT symbol FROM portfolio")
                result = c.fetchall()
                conn.close()

                if not result:
                    print("Your portfolio is empty.")
                    return

                for row in result:
                    symbol = row[0]
                    print(f"\nUpdating {symbol}:")
                    new_qty = int(input("New Quantity: "))
                    new_price = float(input("New Average Price: "))
                    db.update_stocks(symbol, new_qty, new_price)

        except ValueError:
            print("Invalid input. Please enter numeric values.")
        except Exception as e:
            print("Unexpected error:", e)

    def capital_menu(self):
        clear_screen()
        print("1. Add Capital")
        print("2. Withdraw Capital")
        print("3. Set Capital Manually")
        print("4. View Current Capital")
        print("0. Return to Main Menu")

    def run(self):
        db = Database()
        while True:
            self.main_menu()
            try:
                choice = int(input("Enter your choice: "))
            except(ValueError,IndexError):
                print("invalid input")

            if choice == 0:
                print("GoodBye!")
                sys.exit()
            elif choice == 1:
                clear_screen()
                self.capital_menu()
                try:
                    choice = int(input("Enter your choice: "))
                    if choice == 0:
                        continue
                    elif choice == 1:
                        db.add_capital()
                    elif choice == 2:
                        db.withdraw_capital()
                    elif choice == 3:
                        db.set_capital()
                    elif choice == 4:
                        print(f"Your current capital: ₹{db.get_capital()}")

                except(ValueError,IndexError):
                    print("invalid input")

            elif choice == 2:
                clear_screen()
                self.stocks_menu()
                try:
                    choice = int(input("Enter your choice: "))
                    if choice == 0:
                        continue
                    elif choice == 1:
                        self.buy_stocks()
                    elif choice == 2:
                        self.sell_stocks()
                    elif choice == 3:
                        self.update_stocks()

                except(ValueError,IndexError):
                    print("invalid input")

            elif choice == 3:
                clear_screen()
                pass
            elif choice == 4:
                clear_screen()
                db.view_portfolio()