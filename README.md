
# Cli-Portfolio-Tracker

A terminal (CLI) portfolio tracker written in Python.  
This is an interactive command-line tool to manage a simple portfolio (buy/sell/update), store portfolio data in a local SQLite database, log transactions to a CSV file, and write detailed logs to a file.

> This README reflects the current implementation (no external market API is integrated yet — current prices shown in the portfolio view are simulated).

---

## Key features (what the code actually does)

- Interactive CLI menu with:
  - Capital menu: view current capital, add capital, withdraw capital, set capital manually.
  - Stocks menu: buy, sell, and update stocks.
  - View transactions (reads `transactions.csv` and prints a table).
  - View portfolio (reads from SQLite DB and shows current P/L — (**simulated prices**).
- Persistence:
  - Portfolio stored in SQLite database at `../data/portfolio.db`.
  - Capital stored in same SQLite DB (table `capital`, single-row with id=1).
  - Transaction history appended to CSV at `../data/transactions.csv` with headers:
    `date,time,action,symbol,quantity,price,total_price,capital,old_capital`.
  - Logs written to `../data/portfolio_tracker.log`.
- Uses `tabulate` to render prettified tables in the terminal.
- Basic input validation and logging for most user actions.

---

## Quick start / prerequisites

- Python 3.8+ (tested conceptually)
- Required Python package:
```bash
pip install tabulate
````

* Prepare the data directory (the script expects `data/` one level up from the script file):

```bash
# if your script is in the repo root, this creates the expected folder
mkdir -p data
```

> Important: `Config.DATA_DIR` in the code is `os.path.join(BASE_DIR, "..", "data")` — i.e. **one directory above the script file**. Create that `data/` folder before first run to avoid issues with log file creation.

---

## How to run

Place the script file in your workspace (for example `main.py`) and from the folder containing the file run:

```bash
python main.py
```

The app will start the CLI and show a main menu:

```
Main Menu
1 - Capital Menu
2 - Stocks Menu
3 - View Transactions
4 - View Portfolio
0 - Exit
```

Follow prompts to add capital, buy/sell stocks, view portfolio, or view transactions.

---

## Files created / expected

* `../data/portfolio.db` — SQLite database storing:

  * `portfolio` table (`symbol`, `qty`, `avg_price`)
  * `capital` table (single row with id=1 and `amount`)
* `../data/transactions.csv` — Transaction log csv with headers created by `Transactions.ensure()`
* `../data/portfolio_tracker.log` — log file containing debug/info/error messages

---

## Data model & behavior (important details)

* **Buy flow**

  * Prompts: symbol, quantity, price.
  * Checks you have enough `capital` before buying.
  * Decreases capital by `qty * price`, logs transaction to CSV via `Transactions.stock_transact(...)`.
  * If symbol not in DB, inserts it; otherwise updates quantity and recomputes average price.
* **Sell flow**

  * Prompts: symbol, quantity to sell, sell price.
  * Validates symbol existence and quantity sufficiency.
  * Removes the portfolio row when remaining quantity becomes zero, or updates qty when some remains.
  * Adds `sell_qty * sell_price` to capital and logs transaction to CSV.
  * **Note:** current implementation writes sell transactions to CSV using negative numbers for quantity/price/total (the code calls `stock_transact("sell", symbol, -sold_qty, -sell_price, -(sell_price*sold_qty), ...)`). See *Known issues* for details.
* **View portfolio**

  * Reads holdings from DB and calculates P/L using a **simulated current price**:

    ```python
    curr_price = random.uniform(avg_price - (avg_price * 0.05), avg_price + (avg_price * 0.05))
    ```

    That is, current price is randomly chosen within ±5% of stored average price (placeholder until an API is integrated).
* **View transactions**

  * Reads `transactions.csv`, displays as a table with a merged header.
  * After printing it prompts user about export; actual export functionality is not implemented.

---

## Code structure (high-level)

* `clear_screen()` — clears terminal.
* `class Config` — paths (BASE\_DIR, DATA\_DIR, DB\_FILE, CSV\_FILE, LOG\_FILE).
* `class Logger` — logger factory creating file-based loggers (several named loggers created at module import).
* `class Transactions` — CSV creation & append, `stock_transact`, `capital_transact`, `view_transactions`.
* `class Database` — DB connect helper, `create_table`, `get_capital`, `update_capital`, `set/add/withdraw capital`, portfolio CRUD (`insert_stocks`, `update_stocks`, `delete_stock`), `check_symbol`, `view_portfolio`, `total_invested`.
* `class PortfolioTracker` — CLI menus and user interactions: `menu`, `buy_stocks`, `sell_stocks`, `update_stocks`, `run()` loop.

---

## Example transaction CSV row (fields)

`date,time,action,symbol,quantity,price,total_price,capital,old_capital`

Example (BUY):

```
01/01/2025,12:34,BUY,AAPL,10,150.00,1500.00,8500.00,10000.00
```

---

## Known limitations & caveats (being honest about the current code)

These are real things you may want to fix or be aware of:

1. **Data directory / log creation race**

   * The logger's `FileHandler` is created at import time pointing to `../data/portfolio_tracker.log`. If the `data/` directory does not exist, creating the file handler may raise an error. Create the `data/` folder before running the script.

2. **Simulated current prices**

   * `view_portfolio()` uses `random.uniform(...)` to simulate current prices (±5% of avg price). This is a placeholder — real market data must be integrated for accurate P/L.

3. **Sell transaction CSV semantics**

   * The code records sell transactions with negative quantity/price values (`stock_transact("sell", symbol, -sold_qty, -sell_price, ...)`). That can be confusing for CSV readers/analytics. Recommended: log sell transactions with positive numbers and use the `action` column to indicate the type.

4. **Floating point for currency**

   * Money is handled with Python `float` and `round(...)`. For production/finance use, consider `decimal.Decimal` to avoid rounding/precision issues.

5. **`check_symbol` return type**

   * `check_symbol()` returns either `False` or `(True, qty, avg_price)` in current code. This inconsistent return type makes calling code messy. Consider returning `None` or `(qty, avg_price)` consistently.

6. **Transaction export not implemented**

   * After viewing transactions, the app asks if you want to export, but no export functionality exists.

7. **No tests / no CI**

   * There are no unit tests or automated checks included yet.

8. **Single-user local tool**

   * No multi-user or remote operation; database and CSVs are local files.

---

## Suggested next improvements (development roadmap)

* Integrate a market data API (e.g., yfinance, Alpha Vantage, or broker API) to replace simulated prices.
* Fix sell-transaction CSV semantics (log positive quantities/prices).
* Replace float money handling with `decimal.Decimal`.
* Ensure the `data/` directory is created before logger file handler is created.
* Add unit tests for DB operations and transaction writes (use an in-memory sqlite connection for tests).
* Add a `requirements.txt` and a descriptive `README.md` (this file).
* Split code into modules (`config.py`, `logger.py`, `db.py`, `transactions.py`, `cli.py`) and add basic type hints.
* Add a simple CLI flag to run in "demo mode" vs "production mode".
* Add an export feature to CSV/Excel and a simple backup of the DB.

---

## License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/minsariyasoheb/Cli-Portfolio-Tracker/blob/main/LICENSE) file for details.

---

## Contact / author

[Soheb Minsariya](https://github.com/minsariyasoheb)