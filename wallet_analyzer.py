from price_fetcher import PriceFetcher
from transaction_processor import TransactionProcessor
from transaction_fetcher import TransactionFetcher
from data_exporter import DataExporter 
from datetime import datetime

class WalletAnalyzer:
    def __init__(self):
        self.fetcher = TransactionFetcher()
        self.processor = TransactionProcessor()
        self.price_fetcher = PriceFetcher()
        self.exporter = DataExporter()

    def analyze_wallets_and_export(self, wallet_addresses, timeframe, minimum_wallet_capital, minimum_avg_holding_period, minimum_win_rate, minimum_total_pnl, export_filename='analysis_results.csv'):
        """
        Analyzes multiple wallets and exports the results to a CSV file.

        Parameters:
            wallet_addresses (list): A list of wallet addresses to analyze.
            timeframe (str): The timeframe for analysis.
            minimum_wallet_capital (float): The minimum capital required.
            minimum_avg_holding_period (float): The minimum average holding period required.
            minimum_win_rate (float): The minimum win rate required.
            minimum_total_pnl (float): The minimum total PNL required.
            export_filename (str): The name of the CSV file to export results.
        """
        results = []
        
        for address in wallet_addresses:
            result = self.analyze_wallet(address, timeframe, minimum_wallet_capital, minimum_avg_holding_period, minimum_win_rate, minimum_total_pnl)
            if result:
                results.append(result)

        # Export results after analysis
        self.exporter.export_wallet_analysis(results, filename=export_filename)

    def analyze_wallet(self, wallet_address, timeframe, minimum_wallet_capital, minimum_avg_holding_period, minimum_win_rate, minimum_total_pnl):
        if not self.check_wallet_capital(wallet_address, minimum_wallet_capital):
            print(f"Wallet {wallet_address} excluded due to insufficient capital.")
            return None

        transactions = self.fetcher.fetch_transaction_history(wallet_address)
        if not transactions:
            print(f"No transactions found for wallet: {wallet_address}")
            return {
                "address": wallet_address,
                "total_pnl": 0,
                "realized_pnl": 0,
                "unrealized_pnl": 0,
                "win_rate": 0,
                "buy_sell_dates": []
            }

        total_pnl = 0
        realized_pnl = 0
        unrealized_pnl = 0
        profitable_trades = 0
        total_trades = 0
        buy_sell_dates = []

        bought_assets = {}

        for tx in transactions:
            if tx.get("err") is not None:
                print(f"Skipping transaction {tx['signature']} due to errors.")
                continue

            details = self.fetcher.fetch_transaction_details(tx['signature'])
            if not details:
                print(f"Error fetching details for transaction {tx['signature']}.")
                continue

            timestamp = details['blockTime']
            transaction_datetime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            # Skip pre-timeframe transactions
            if not self.is_within_timeframe(timestamp, timeframe):
                continue

            is_buy = "buy_condition" in details  # Replace with actual logic to detect buy
            is_sell = "sell_condition" in details  # Replace with actual logic to detect sell

            # Handle buy transactions
            if is_buy:
                amount = details.get("amount", 0)  # Replace with actual transaction amount
                price = self.price_fetcher.get_sol_to_usd_price()  # Fetch current price of SOL
                unrealized_pnl -= amount * price
                bought_assets[details["token_id"]] = {"price": price, "amount": amount, "timestamp": timestamp}
                buy_sell_dates.append({'transaction': 'buy', 'datetime': transaction_datetime})

            # Handle sell transactions
            elif is_sell:
                amount = details.get("amount", 0)  # Replace with actual transaction amount
                price = self.price_fetcher.get_sol_to_usd_price()  # Fetch current price of SOL
                realized_pnl += amount * price
                profitable_trades += 1 if amount * price > 0 else 0
                buy_sell_dates.append({'transaction': 'sell', 'datetime': transaction_datetime})

            total_trades += 1

        total_pnl = realized_pnl + unrealized_pnl
        win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0

        # Exclude based on win rate and total PNL criteria
        if win_rate < minimum_win_rate or total_pnl < minimum_total_pnl:
            print(f"Wallet {wallet_address} excluded due to low win rate or PNL.")
            return None

        avg_holding_period = self.calculate_avg_holding_period(buy_sell_dates)
        if avg_holding_period < minimum_avg_holding_period:
            print(f"Wallet {wallet_address} excluded due to short average holding period.")
            return None

        return {
            "address": wallet_address,
            "total_pnl": total_pnl,
            "realized_pnl": realized_pnl,
            "unrealized_pnl": unrealized_pnl,
            "win_rate": win_rate,
            "settings": {}  # Add settings used for analysis here if applicable
        }

    def check_wallet_capital(self, address, minimum_capital_usd):
        sol_balance = self.fetcher.fetch_wallet_balance(address)
        sol_to_usd = self.price_fetcher.get_sol_to_usd_price()
        
        if sol_to_usd == 0:
            return False
        
        wallet_balance_usd = sol_balance * sol_to_usd
        print(f"Wallet {address} balance: {wallet_balance_usd:.2f} USD (SOL: {sol_balance:.2f})")
        
        return wallet_balance_usd >= minimum_capital_usd

    def is_within_timeframe(self, tx_timestamp, timeframe):
        current_time = datetime.now()
        delta_days = (current_time - datetime.fromtimestamp(tx_timestamp)).days
        
        if timeframe == '1':
            return delta_days <= 30
        elif timeframe == '3':
            return delta_days <= 90
        elif timeframe == '6':
            return delta_days <= 180
        elif timeframe == '12':
            return delta_days <= 365
        else:
            return True

    def calculate_avg_holding_period(self, buy_sell_dates):
        holding_periods = []
        
        for i in range(1, len(buy_sell_dates), 2):  
            buy_time = datetime.strptime(buy_sell_dates[i-1]['datetime'], '%Y-%m-%d %H:%M:%S')
            sell_time = datetime.strptime(buy_sell_dates[i]['datetime'], '%Y-%m-%d %H:%M:%S')
            holding_period = (sell_time - buy_time).total_seconds() / 60  
            holding_periods.append(holding_period)

        return sum(holding_periods) / len(holding_periods) if holding_periods else 0
