import os
import csv
from datetime import datetime
from app.config import Config
from app.logger import Logger

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

        with open(self.file, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            rows = list(reader)  # Read all rows into memory

            if not rows:
                print("Error: You do not have any Transactions")
                transact_log.warning("No transactions in the file")
                return

            print("\n--- Transaction History ---")
            for row in rows:
                print("\n", end="")
                for field in self.fieldnames:
                    print(row.get(field, ""), end=" ")
            print("\n----------------------------")