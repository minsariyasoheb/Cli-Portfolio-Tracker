import random
import sys
import os
import logging
from datetime import datetime


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class PortfolioTracker():
    def __init__(self):
        self.transactions = []
        self.portfolio = {}

    def menu(self):
        print("1. Add Stocks")
        print("2. Remove Stocks")
        print("3. View Transactions")
        print("4. View Portfolio")
        print("5. Check Past Performance")
        print("0. Exit")
    
    def add_stocks(self):
        symbol = input("Enter symbol name\n-> ").upper()
        try:
            qty = int(input("How many did you buy?\n-> "))
            price = float(input("How much was each stock?\n-> "))
            now = datetime.now().strftime("%d/%m/%y %H:%M")
            self.transactions.append((now, symbol, qty, price*qty))
            if symbol not in self.portfolio:
                self.portfolio[symbol] = {"Quantity": qty, "Avg Price": price, "Current Price": random.uniform(10, 20)}
            else:
                old_qty = self.portfolio[symbol]["Quantity"]
                old_price = self.portfolio[symbol]["Avg Price"]
                
                new_qty = old_qty + qty
                new_avg_price = ((old_qty * old_price) + (qty * price)) / new_qty
                
                self.portfolio[symbol]["Quantity"] = new_qty
                self.portfolio[symbol]["Avg Price"] = round(new_avg_price, 2)
        except(ValueError,IndexError):
            print("Error: invalid input")

    def remove_stocks(self):
        symbol = input("Which stock (symbol) did you sell?\n-> ").upper()
        
        if symbol not in self.portfolio:
            print("Error: Symbol does not exist")
            return

        try:
            qty = int(input("How many did you sell?\n-> "))
            
            if qty > self.portfolio[symbol]["Quantity"]:
                print("Error: Selling quantity cannot exceed existing quantity")
                return

            price = float(input("At what price did you sell each?\n-> "))
            now = datetime.now().strftime("%d/%m/%y %H:%M")
            
            # Log the sell transaction
            self.transactions.append((now, symbol, -qty, -price * qty))

            # Update portfolio
            self.portfolio[symbol]["Quantity"] -= qty

            # If all shares sold, remove from portfolio
            if self.portfolio[symbol]["Quantity"] == 0:
                del self.portfolio[symbol]

        except ValueError:
            print("Invalid input")
        
    def view_transactions(self):
        print(f"{'Date':<20}{'Symbol':<12}{'Quantity':>10}{'Dr/Cr':>13}")
        print("-" * 55)
        sum = 0
        total_qty = 0
        for date, symbol, qty, dr_cr in self.transactions:
            print(f"{date:<20}{symbol:<12}{qty:>10}{dr_cr:>13.2f}")
            sum += dr_cr
            total_qty += qty
        print("=" * 55)
        print(f"{total_qty:>42}{sum:>13.2f}")
        print("-" * 55)
    
    def view_portfolio(self):
        print(f"{'Symbol':<10}{'Quantity':>10}{'Avg Price':>15}{'Curr Price':>15}{'P/L':>12}")
        print("-" * 67)
        total_pnl = 0
        for symbol, data in self.portfolio.items():
            qty = data["Quantity"]
            avg_price = data["Avg Price"]
            curr_price = data["Current Price"]
            stock_pnl = (curr_price - avg_price) * qty
            total_pnl += stock_pnl
            print(f"{symbol:<10}{qty:>10}{avg_price:>15.2f}{curr_price:>15.2f}{stock_pnl:>12.2f}")
        print("=" * 67)
        print(f"{'Total P/L:':>50}{total_pnl:>12.2f}")
        print("-" * 67)

    
    def run(self):
        while True:
            self.menu()
            try:
                choice = int(input("Enter your choice: "))
            except(ValueError,IndexError):
                print("invalid input")

            if choice == 0:
                print("GoodBye!")
                sys.exit()
            elif choice == 1:
                self.add_stocks()
            elif choice == 2:
                self.remove_stocks()
            elif choice == 3:
                clear_screen()
                self.view_transactions()
            elif choice == 4:
                self.view_portfolio()
            elif choice == 5:
                pass
        
if __name__ == "__main__":
    app = PortfolioTracker()
    app.run()