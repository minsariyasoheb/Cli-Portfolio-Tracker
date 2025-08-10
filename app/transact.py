import os
import csv
from app.config import Config
from app.logger import Logger
from tabulate import tabulate
from datetime import datetime

class Transactions:
    def __init__(self):
        self.file = Config.CSV_FILE
        self.fieldnames = [
            "date", "time", "action", "symbol", "quantity",
            "price", "total_price", "capital", "old_capital"
        ]
        self.ensure()

    def ensure(self):
        # Check if file exists
        if not os.path.exists(self.file) or os.path.getsize(self.file) == 0:
            # Open file in write mode and add headers
            with open(self.file, mode='w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()

    def stock_transact(self, action, symbol, quantity, price, total_price, capital, old_capital):
        date = datetime.now().strftime("%d/%m/%Y")
        time = datetime.now().strftime("%H:%M")

        row = {
            "date": date,
            "time": time,
            "action": action,
            "symbol": symbol,
            "quantity": quantity,
            "price": f"{round(price, 2):.2f}",
            "total_price": f"{round(total_price, 2):.2f}",
            "capital": f"{round(capital, 2):.2f}",
            "old_capital": f"{round(old_capital, 2):.2f}"
        }

        with open(self.file, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerow(row)

    def capital_transact(self, action, capital, old_capital):
        date = datetime.now().strftime("%d/%m/%Y")
        time = datetime.now().strftime("%H:%M")

        row = {
            "date": date,
            "time": time,
            "action": action,
            "symbol": "N/A",
            "quantity": "N/A",
            "price": "N/A",
            "total_price": "N/A",
            "capital": f"{round(capital, 2):.2f}",
            "old_capital": f"{round(old_capital, 2):.2f}"
        }

        with open(self.file, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerow(row)

    def view_transactions(self):
        transact_log = Logger.loggers["transact"]

        try:
            with open(self.file, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                rows = list(reader)  # Read all rows into memory

                if not rows:
                    print("Error: You do not have any Transactions")
                    transact_log.warning("No transactions in the file")
                    return

                # Create the table
                table_str = tabulate(rows, headers="keys", tablefmt="fancy_grid")

                # Find table width from first line
                table_width = len(table_str.split("\n")[0])

                # Create merged header box
                top_border = "╒" + "═" * (table_width - 2) + "╕"
                title = "TRANSACTION HISTORY".center(table_width - 2)
                title_line = f"│{title}│"

                # Print final table with title
                print(top_border)
                print(title_line)
                print(table_str)

                action = input("\n\nThere's no export available yet, just type 'n' for now, update will be available soon\nDo You want to export? (y/n)")
        except FileNotFoundError:
            print(f"Error: File '{self.file}' not found.")
            transact_log.error(f"Transaction file '{self.file}' not found.")