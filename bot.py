import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from decouple import config
from api_client import APIClient
from wallet_analyzer import WalletAnalyzer
from transaction_fetcher import TransactionFetcher

class Bot:
    def __init__(self):
        self.analyzer = WalletAnalyzer()
        self.api_client = APIClient()  # Create an instance of APIClient
        self.transaction_fetcher = TransactionFetcher()
        self.helius_rpc_url = config('HELIUS_RPC_URL')
        self.token_program_id = config('TOKEN_PROGRAM_ID')

    def fetch_wallet_addresses(self, from_csv=False, csv_filename='addresses.csv'):
        """
        Fetches wallet addresses either dynamically or from a CSV file.

        Parameters:
            from_csv (bool): Whether to fetch wallet addresses from a CSV file.
            csv_filename (str): The name of the CSV file to fetch wallet addresses from.

        Returns:
            list: A list of wallet public keys.
        """
        if from_csv:
            return self.load_wallet_addresses_from_csv(csv_filename)
        else:
            return self.fetch_wallet_addresses_dynamically()

    def fetch_wallet_addresses_dynamically(self):
        """
        Fetches wallet addresses dynamically.

        Returns:
            list: A list of wallet public keys.
        """
        successful_wallets = []
        initial_wallet = "5oNDL3swdJJF1g9DzJiZ4ynHXgszjAEpUkxVYejchzrY"
        
        token_accounts = self.api_client.get_token_accounts_by_owner(initial_wallet)
        
        if token_accounts:
            successful_wallets.extend([account['pubkey'] for account in token_accounts])
        
        return successful_wallets

    def load_wallet_addresses_from_csv(self, file_path):
        """
        Loads wallet addresses from a CSV file.

        Parameters:
            file_path (str): The path to the CSV file containing wallet addresses.

        Returns:
            list: A list of wallet addresses loaded from the CSV file.
        """
        try:
            df = pd.read_csv(file_path)
            wallet_addresses = df.iloc[:, 0].tolist()  # Assuming the wallet address is in the first column
            print(f"Wallet addresses loaded from {file_path}")
            return wallet_addresses
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' does not exist.")
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return []

    def save_wallet_addresses_to_csv(self, wallet_addresses, file_path):
        """
        Saves wallet addresses and their token balances to a CSV file.

        Parameters:
            wallet_addresses: A list of wallet addresses to save.
            file_path: The path where the CSV file will be saved.
        """
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_wallet = {executor.submit(self.api_client.get_token_accounts_by_owner, wallet): wallet for wallet in wallet_addresses}
            results = []
            for future in as_completed(future_to_wallet):
                wallet = future_to_wallet[future]
                try:
                    tokens = future.result()
                    for token, balance in tokens.items():
                        results.append({'wallet_address': wallet, 'token_address': token, 'balance': balance})
                except Exception as e:
                    print(f"Error processing wallet {wallet}: {e}")

        df = pd.DataFrame(results)
        df.to_csv(file_path, index=False)
        print(f"Wallet addresses and token balances saved to {file_path}")

    def run(self, from_csv=False, csv_filename='wallet_addresses.csv', timeframe='1', minimum_wallet_capital=1000, minimum_avg_holding_period=30, minimum_win_rate=50, minimum_total_pnl=100, export_filename='results.csv'):
        """
        Analyzes wallets and exports the results to a CSV file.
        
        Parameters:
            from_csv (bool): Whether to fetch wallet addresses from a CSV file.
            csv_filename (str): The name of the CSV file to fetch wallet addresses from.
            timeframe (str): The timeframe for analysis.
            minimum_wallet_capital (float): The minimum capital required.
            minimum_avg_holding_period (float): The minimum average holding period required.
            minimum_win_rate (float): The minimum win rate required.
            minimum_total_pnl (float): The minimum total PNL required.
            export_filename (str): The name of the CSV file to export results.
        """
        print("Starting wallet analysis...")

        # Fetch wallet addresses
        wallet_addresses = self.fetch_wallet_addresses(from_csv, csv_filename)

        if not wallet_addresses:
            print("No wallet addresses found. Exiting.")
            return

        # Save wallet addresses and their token balances to CSV
        self.save_wallet_addresses_to_csv(wallet_addresses, export_filename)

        # Analyze wallets and export results
        self.analyzer.analyze_wallets_and_export(
            wallet_addresses,
            timeframe,
            minimum_wallet_capital,
            minimum_avg_holding_period,
            minimum_win_rate,
            minimum_total_pnl,
            export_filename
        )
        print(f"Analysis complete. Results exported to '{export_filename}'.")

if __name__ == "__main__":
    bot = Bot()
    bot.run(from_csv=True, csv_filename='addresses.csv')