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
                self.portfolio[symbol] = {"Quantity": qty, "Avg Price": price}
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
        print("Date\t\tSymbol\tQty\tDr/Cr")
        for i in self.transactions:
            print(f"{i[0]}\t{i[1]}\t{i[2]}\t{i[3]}")
        print()
    
    def view_portfolio(self):
        print("Symbol\tQty\tPer Price")
        for i in self.portfolio:
            print(f"{i}", end="")
            for j in self.portfolio[i]:
                print(f"\t{self.portfolio[i][j]}", end="")
            print()
    
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