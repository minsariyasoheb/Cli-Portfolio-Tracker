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

        symbol = input("Enter symbol name\n-> ").upper()
        try:
            qty = int(input("How many did you buy?\n-> "))
            price = float(input("How much was each stock?\n-> "))
            now = datetime.now().strftime("%d/%m/%y %H:%M")

            result = db.check_symbol(symbol)
            if result is False:
                # New symbol
                self.portfolio[symbol] = {
                    "Quantity": qty,
                    "Avg Price": price,
                    "Current Price": random.uniform(10, 20)
                }
                db.insert_stocks(symbol, qty, price)
                self.transactions.append((now, symbol, qty, price * qty))

            else:
                # Symbol already exists, update quantity and average price
                exists, old_qty, old_price = result
                del exists
                new_qty = old_qty + qty
                new_avg_price = ((old_qty * old_price) + (qty * price)) / new_qty
                new_avg_price = round(new_avg_price, 2)

                # Update in memory
                if symbol in self.portfolio:
                    self.portfolio[symbol]["Quantity"] = new_qty
                    self.portfolio[symbol]["Avg Price"] = new_avg_price
                else:
                    self.portfolio[symbol] = {
                        "Quantity": new_qty,
                        "Avg Price": new_avg_price,
                        "Current Price": random.uniform(10, 20)
                    }

                # Update in DB
                db.update_stocks(symbol, new_qty, new_avg_price)
                self.transactions.append((now, symbol, qty, price * qty))

        except Exception as e:
            print("Error:", e)

    def capital_menu(self):
        clear_screen()
        print("1. Add Capital")
        print("2. Withdraw Capital")
        print("3. Set Capital Manually")
        print("4. View Current Capital")
        print("0. Return to Main Menu")

    def add_capital(self):
        if self.capital == 0:
            try:
                self.capital = float(input("Enter your initial capital:\n→ "))
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                return
        elif self.capital > 0:
            print(f"Your current capital: ₹{self.capital}")
            try:
                additional_amount = float(input("How much capital would you like to add?\n→ "))
                self.capital += additional_amount
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                return
        else:
            print("Invalid capital value. Please reset your capital.")

    def withdraw_capital(self):
        if self.capital == 0:
            print("Error: Cannot withdraw capital because your existing capital is ₹0.\nPlease add capital first.")
            return
        elif self.capital > 0:
            print(f"Your current capital: ₹{self.capital}")
            try:
                withdrawal_amount = float(input("How much capital would you like to withdraw?\n→ "))
                if withdrawal_amount > self.capital:
                    print("Error: You cannot withdraw more than your current capital.")
                    return
                self.capital -= withdrawal_amount
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                return
        else:
            print("Invalid capital value. Please reset your capital.")

    def set_capital(self):
        print(f"Your current capital: ₹{self.capital}")
        try:
            self.capital = float(input("Enter your new capital amount:\n→ "))
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return


    def run(self):
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
                except(ValueError,IndexError):
                    print("invalid input")

                    if choice == 0:
                        continue
                    elif choice == 1:
                        self.add_capital()
                    elif choice == 2:
                        self.withdraw_capital()
                    elif choice == 3:
                        self.set_capital()
                    elif choice == 4:
                        print(f"Your current capital: ₹{self.capital}")

            elif choice == 2:
                self.stocks_menu()
                try:
                    choice = int(input("Enter your choice: "))
                except(ValueError,IndexError):
                    print("invalid input")
                
                if choice == 0:
                    continue
                elif choice == 1:
                    self.buy_stocks()

            elif choice == 3:
                pass
            elif choice == 4:
                db = Database()
                db.view_portfolio()