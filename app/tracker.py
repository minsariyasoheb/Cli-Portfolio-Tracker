import random
import sys
import os
from app.logger import Logger
from app.database import Database
from app.transact import Transactions
from tabulate import tabulate
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class PortfolioTracker():
    def __init__(self):
        self.transact = Transactions()
        self.db = Database()
        self.db.create_table()

    def menu(self, num):    # All Menus
        def default(menu_items, header):    # Defaults for all menus
            headers = ["Option", header]
            table_str = tabulate(menu_items, headers=headers, tablefmt="rounded_grid")
            return table_str

        def main(): # Main menu
            header = "Main Menu"
            menu_items = [
                ["1", "Capital Menu"],
                ["2", "Stocks Menu"],
                ["3", "View Transactions"],
                ["4", "View Portfolio"],
                ["0", "Exit"]
            ]
            print(default(menu_items, header))

        def capital():  # Capital Menu
            clear_screen()
            logger = Logger.loggers["main"]
            header = "Capital Menu"
            menu_items = [
                ["1", "View Current Capital"],
                ["2", "Add Capital"],
                ["3", "Withdraw Capital"],
                ["4", "Set Capital Manually"],
                ["0", "Return to Main Menu"]
            ]
            print(default(menu_items, header))
            try:
                choice = int(input("Enter your choice: "))
                logger.debug(f"Capital menu choice entered: {choice}")
                if choice == 0:
                    clear_screen()
                    return
                elif choice == 1:
                    clear_screen()
                    capital = self.db.get_capital()
                    table = [["Current Capital", f"₹{capital}"]]
                    print(tabulate(table, tablefmt="fancy_grid"))
                    logger.info(f"Viewed capital: ₹{capital}")
                elif choice == 2:
                    clear_screen()
                    self.db.add_capital()
                    logger.info("Capital Added")
                
                elif choice == 3:
                    clear_screen()
                    self.db.withdraw_capital()
                    logger.info("Capital Withdrawn")

                elif choice == 4:
                    clear_screen()
                    self.db.set_capital()
                    logger.info("Capital Withdrawn")

                else:
                    clear_screen()
                    print("Invalid input")
                    return
            except (ValueError, IndexError):
                clear_screen()
                print("Invalid input")
                logger.warning("Non-numeric or out-of-range input at main menu")
                return

        def stocks():   # Stocks Menu
            clear_screen()
            logger = Logger.loggers["main"]
            header = "Stocks Menu"
            menu_items = [
                ["1", "Buy Stocks"],
                ["2", "Sell Stocks"],
                ["3", "Update Stock Details"],
                ["0", "Return to Main Menu"]
            ]
            print(default(menu_items, header))
            try:
                choice = int(input("Enter your choice: "))
                logger.debug(f"Stocks menu choice entered: {choice}")
                if choice == 0:
                    clear_screen()
                    return
                elif choice == 1:
                    clear_screen()
                    self.buy_stocks()
                elif choice == 2:
                    clear_screen()
                    self.sell_stocks()
                elif choice == 3:
                    clear_screen()
                    logger = Logger.loggers["main"]
                    header = "Update Stocks Menu"
                    menu_items = [
                        ["1", "Add Multiple Stocks"],
                        ["2", "Update All Stocks"],
                        ["0", "Return to Main Menu"]
                    ]
                    print(default(menu_items, header))
                    self.update_stocks()
                else:
                    clear_screen()
                    print("Idk what number was that but that is not available rn")
                    return
            except (ValueError, IndexError):
                clear_screen()
                print("Invalid input")
                logger.warning("Non-numeric or out-of-range input at main menu")
                return

        if num == 0:
            main()
        elif num == 1:
            capital()
        elif num == 2:
            stocks()
        else:
            clear_screen()
            print("Idk what number was that but that is not available rn")
            return
        
    def buy_stocks(self):
        capital = self.db.get_capital()

        logger = Logger.loggers["buy"]
        logger.debug("Buy stocks menu opened")
        transact_log = Logger.loggers["transact"]
        symbol = input("Enter symbol name you want to buy (e.g. APPL for Apple, GOOG for Google etc.)\n-> ").upper()
        try:
            qty = int(input("How many did you buy?\n-> "))
            if qty <= 0:
                print("Error: Buying quantity cannot be 0 or less than 0")
                logger.warning(f"Tried to buy stock '{symbol}' with invalid quantity: {qty}")
                return

            price = float(input("How much was each stock?\n-> "))
            if price <= 0:
                print("Error: Buying price cannot be 0 or less than 0")
                logger.warning(f"Tried to buy stock '{symbol}' with invalid price: {price}")
                return

            total_cost = qty * price
            if total_cost > capital:
                print("Error: You do not have enough capital to buy this stock")
                logger.warning(
                    f"Insufficient capital. Tried to buy {qty} x {symbol} at ₹{price:.2f} each. Capital: ₹{capital:.2f}"
                )
                return

            remaining_capital = capital - total_cost
            self.db.update_capital(remaining_capital)
            logger.info(
                f"Purchased {qty} x {symbol} at ₹{price:.2f}. Total: ₹{total_cost:.2f}. Capital left: ₹{remaining_capital:.2f}"
            )
            data = [
                ["Symbol", symbol],
                ["Quantity", qty],
                ["Price", f"₹{price:.2f}"],
                ["Total Cost", f"₹{total_cost:.2f}"],
                ["Capital Left", f"₹{remaining_capital:.2f}"]
            ]

            print(tabulate(data, headers=["Detail", "Value"], tablefmt="fancy_grid"))
            self.transact.stock_transact("BUY", symbol,qty,price,total_cost,remaining_capital,capital)
            transact_log.info("Transaction Successful")

            result = self.db.check_symbol(symbol)
            if result is False:
                self.db.insert_stocks(symbol, qty, price)
                logger.debug(f"Inserted new stock '{symbol}' into portfolio: {qty} shares at ₹{price:.2f}")
            else:
                # Symbol already exists, update quantity and average price
                exists, old_qty, old_price = result
                del exists
                new_qty = old_qty + qty
                new_avg_price = ((old_qty * old_price) + (qty * price)) / new_qty
                new_avg_price = round(new_avg_price, 2)

                self.db.update_stocks(symbol, new_qty, new_avg_price)
                logger.debug(
                    f"Updated stock '{symbol}': Old Qty: {old_qty}, New Qty: {new_qty}, "
                    f"Old Avg Price: ₹{old_price:.2f}, New Avg Price: ₹{new_avg_price:.2f}"
                )

        except ValueError:
            print("Invalid input. Please enter valid numbers.")
            logger.error("Invalid input for quantity or price. ValueError occurred.")

        except Exception as e:
            print("Error:", e)
            logger.exception(f"Unexpected error occurred while buying stock '{symbol}': {e}")

    def sell_stocks(self):
        logger = Logger.loggers["sell"]
        transact_log = Logger.loggers["transact"]
        logger.debug("Sell stocks menu opened")

        symbol = input("Enter symbol name\n-> ").upper()
        result = self.db.check_symbol(symbol)

        if result is False:
            print("Error: Symbol does not exist")
            logger.warning(f"Tried to sell stock '{symbol}' which does not exist in portfolio")
            return

        exists, qty, price = result
        del exists

        try:
            sold_qty = int(input("How many did you sell?\n-> "))
            if sold_qty > qty:
                print("Error: Selling quantity cannot exceed existing quantity")
                logger.warning(f"Tried to sell {sold_qty} of '{symbol}', but only {qty} available")
                return

            sell_price = float(input("How much was each stock?\n-> "))
            if sold_qty <= 0 or sell_price <= 0:
                print("Error: Quantity and price must be positive numbers")
                logger.warning(f"Invalid sell attempt for '{symbol}': qty={sold_qty}, price={sell_price}")
                return

            remaining_qty = qty - sold_qty
            profit_or_loss = (sell_price - price) * sold_qty

            if remaining_qty == 0:
                self.db.delete_stock(symbol)
                logger.info(f"Sold all shares of '{symbol}' ({sold_qty} units at ₹{sell_price:.2f}). Removed from portfolio.")
            else:
                self.db.update_stocks(symbol, remaining_qty, price)
                logger.info(f"Sold {sold_qty} of '{symbol}' at ₹{sell_price:.2f}. Remaining: {remaining_qty} shares.")

            capital_before = self.db.get_capital()
            new_capital = capital_before + (sell_price * sold_qty)
            self.db.update_capital(new_capital)
            logger.debug(
                f"Capital updated from ₹{capital_before:.2f} to ₹{new_capital:.2f} "
                f"after selling {sold_qty} x {symbol} at ₹{sell_price:.2f} (P/L: ₹{profit_or_loss:.2f})"
            )
            
            data = [[symbol, sold_qty, f"{sell_price:.2f}", f"{profit_or_loss:.2f}"]]

            print(tabulate(
                data,
                headers=["Symbol", "Qty Sold", "Sell Price (₹)", "P/L (₹)"],
                tablefmt="fancy_grid"
            ))

            self.transact.stock_transact("sell", symbol,-sold_qty,-sell_price,-(sell_price*sold_qty),new_capital,capital_before)
            transact_log.info("Transaction Successful")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")
            logger.error(f"Invalid input while selling '{symbol}'. ValueError occurred.")

        except Exception as e:
            print("Error:", e)
            logger.exception(f"Unexpected error occurred while selling stock '{symbol}': {e}")

    def update_stocks(self):
        logger = Logger.loggers["update"]

        try:
            choice = int(input("\n-> "))
            logger.debug(f"Entered update_stocks with choice: {choice}")

            if choice == 0:
                clear_screen()
                logger.info("Exited stock update menu")
                return

            elif choice == 1:
                num = int(input("How many stocks do you want to add?\n-> "))
                logger.debug(f"Adding {num} new stock(s) to portfolio")

                for i in range(1, num + 1):
                    print(f"\nStock #{i}")
                    symbol = input("Enter symbol name\n-> ").upper()
                    qty = int(input("How many did you buy?\n-> "))
                    if qty <= 0:
                        print("Error: Quantity must be > 0.")
                        logger.warning(f"Attempted to add '{symbol}' with non-positive qty: {qty}")
                        return
                    price = float(input("What was the price per stock?\n-> "))
                    if price <= 0:
                        print("Error: Price must be > 0.")
                        logger.warning(f"Attempted to add '{symbol}' with non-positive price: ₹{price}")
                        return
                    self.db.insert_stocks(symbol, qty, price)
                    logger.info(f"Added stock '{symbol}' with qty={qty}, price=₹{price:.2f}")
                print("Your new portfolio:")
                self.db.view_portfolio()

            elif choice == 2:
                clear_screen()
                print("Your current portfolio:")
                self.db.view_portfolio()
                logger.debug("Fetching portfolio for bulk update")

                conn = self.db.get_db_connection()
                c = conn.cursor()
                c.execute("SELECT symbol FROM portfolio")
                result = c.fetchall()
                conn.close()

                for row in result:
                    symbol = row[0]
                    print(f"\nUpdating {symbol}:")
                    new_qty = int(input("New Quantity: "))
                    new_price = float(input("New Average Price: "))

                    if new_qty <= 0 or new_price <= 0:
                        print("Error: Quantity and price must be > 0.")
                        logger.warning(f"Invalid update for '{symbol}' → qty={new_qty}, price=₹{new_price}")
                        continue

                    self.db.update_stocks(symbol, new_qty, new_price)
                    logger.info(f"Updated stock '{symbol}' → qty={new_qty}, avg_price=₹{new_price:.2f}")
                print("Your new portfolio:")
                self.db.view_portfolio()

        except ValueError:
            print("Invalid input. Please enter numeric values.")
            logger.error("ValueError: Non-numeric input provided")
        except Exception as e:
            print("Unexpected error:", e)
            logger.exception(f"Exception in update_stocks(): {e}")


    def run(self):
        logger = Logger.loggers["main"]
        transact = Transactions()
        while True:
            self.menu(0)
            try:
                choice = int(input("Enter your choice: "))
                logger.debug(f"Main menu choice entered: {choice}")
                if choice == 0:
                    print("Goodbye!")
                    sys.exit()
                elif choice == 3:
                    clear_screen()
                    transact.view_transactions()
                else:
                    clear_screen()
                    self.menu(choice)

            except (ValueError, IndexError):
                clear_screen()
                print("Invalid input")
                logger.warning("Non-numeric or out-of-range input at main menu")
                continue