import requests
import csv
import json
import time
import random
from datetime import datetime, timezone
import os
from decouple import config  # For loading environment variables

# Load API endpoints from the environment file
HELIUS_RPC_URL = config("HELIUS_RPC_URL")
HELIUS_PARSE_URL = config("HELIUS_PARSE_URL")
HELIUS_TRANSACTION_PARSE_URL = config("HELIUS_TRANSACTION_PARSE_URL")
SOLANA_RPC_URL = config("SOLANA_RPC_URL")

# Define which API to use (toggle as needed)
USE_HELIUS = False  # Set to True for Helius, False for Solana Public RPC
API_ENDPOINT = HELIUS_RPC_URL if USE_HELIUS else SOLANA_RPC_URL
BATCH_SIZE = 2 # Number of transactions to fetch per batch

# Function to send a POST request to the Solana API with retry logic and version handling
def post_request(method, params):
    headers = {"Content-Type": "application/json"}
    data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    retries = 2  # Retry up to 2 times for each request
    backoff_time = 1  # Start with a 1-second backoff for 429 errors
    for attempt in range(retries):
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        result = response.json()

        # Handle rate limiting error (429)
        if response.status_code == 429:
            print(f"Rate limit exceeded (attempt {attempt+1}/{retries}). Retrying in {backoff_time:.2f} seconds...")
            time.sleep(backoff_time)  # Exponential backoff
            backoff_time = min(backoff_time * 2, 32)  # Max 32 seconds delay before retrying

        # Handle transaction version error (-32015)
        elif 'error' in result and result['error']['code'] == -32015:
            print(f"Transaction version not supported. Skipping transaction {params[0]}.")
            return None  # Skip unsupported transaction

        # If no error, return result
        elif response.status_code == 200:
            return result
        else:
            print(f"Unexpected error (attempt {attempt+1}/{retries}): {response.status_code}, {json.dumps(result, indent=2)}")
            return None

    print("Exceeded retry limit for this request. Skipping transaction.")
    return None


# Fetch transaction history in batches
def fetch_transaction_history(address, batch_size=BATCH_SIZE):
    """
    Fetches the transaction history for a given address in specified batch sizes.
    
    Parameters:
        address (str): The address for which to fetch transaction history.
        batch_size (int): The number of transactions to fetch per batch.
        
    Returns:
        list: A list of transactions fetched.
    """

    all_transactions = []
    before_signature = None
    while True:
        params = [address, {"limit": batch_size}]
        if before_signature:
            params[1]["before"] = before_signature

        result = post_request("getSignaturesForAddress", params)
        if not result or "result" not in result:
            print(f"Error fetching transactions for {address}.")
            break
        
        transactions = result["result"]
        if not transactions:
            break  # No more transactions to fetch

        all_transactions.extend(transactions)
        before_signature = transactions[-1]["signature"]

        if len(transactions) < batch_size:
            break  # Reached the end of available transactions

    print(f"Fetched {len(all_transactions)} transactions for {address}.")
    return all_transactions


# Function to fetch transaction details
def fetch_transaction_details(signature):
    result = post_request("getTransaction", [signature, {"encoding": "jsonParsed"}])
    if not result:
        return None
    return result.get("result", None)


# Process and filter transactions
def filter_transactions(address, timeframe):
    all_transactions = fetch_transaction_history(address)
    filtered_transactions = []

    for tx in all_transactions:
        # Skip transactions with errors
        if tx.get("err"):
            print(f"Transaction {tx['signature']} skipped due to error: {tx['err']}")
            continue

        # Fetch transaction details
        details = fetch_transaction_details(tx["signature"])
        if not details:
            print(f"Transaction {tx['signature']} skipped due to missing details.")
            continue

        # Check if transaction is within the timeframe
        if not is_within_timeframe(details["blockTime"], timeframe):
            continue

        # Determine transaction type (replace with actual conditions)
        is_buy = "buy_condition" in details  # Replace with real condition for "buy"
        is_sell = "sell_condition" in details  # Replace with real condition for "sell"

        if is_buy or is_sell:
            transaction_type = "buy" if is_buy else "sell"
            filtered_transactions.append({
                "signature": tx["signature"],
                "type": transaction_type,
                "timestamp": details["blockTime"]
            })
        else:
            print(f"Transaction {tx['signature']} skipped (not buy or sell).")
    
    print(f"Filtered {len(filtered_transactions)} buy/sell transactions for {address}.")
    return filtered_transactions


# Placeholder function to fetch token price
def get_token_price(token_symbol):
    return 1.0  # Replace with actual price fetching logic

# Function to convert Unix timestamp to human-readable date and time
def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# Function to fetch the wallet balance in SOL
def fetch_wallet_balance(address):
    result = post_request("getBalance", [address])
    
    if result and "result" in result:
        sol_balance = result["result"]["value"] / 10**9  # Convert lamports to SOL (1 SOL = 10^9 lamports)
        return sol_balance
    else:
        print(f"Error fetching balance for {address}")
        return 0

# Function to fetch SOL to USD conversion rate from CoinGecko
def get_sol_to_usd_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data["solana"]["usd"]
    else:
        print("Error fetching SOL price in USD")
        return 0

# Function to check wallet capital in USD
def check_wallet_capital(address, minimum_capital_usd):
    sol_balance = fetch_wallet_balance(address)
    sol_to_usd = get_sol_to_usd_price()
    
    if sol_to_usd == 0:
        return False  # If price fetch failed, return False
    
    wallet_balance_usd = sol_balance * sol_to_usd
    print(f"Wallet {address} balance: {wallet_balance_usd:.2f} USD (SOL: {sol_balance:.2f})")
    
    return wallet_balance_usd >= minimum_capital_usd

# Function to calculate the average holding period
def calculate_avg_holding_period(buy_sell_dates):
    holding_periods = []
    for i in range(1, len(buy_sell_dates), 2):  # Assuming alternating buy/sell transactions
        buy_time = datetime.strptime(buy_sell_dates[i-1]['datetime'], '%Y-%m-%d %H:%M:%S')
        sell_time = datetime.strptime(buy_sell_dates[i]['datetime'], '%Y-%m-%d %H:%M:%S')
        holding_period = (sell_time - buy_time).total_seconds() / 60  # In minutes
        holding_periods.append(holding_period)
    return sum(holding_periods) / len(holding_periods) if holding_periods else 0

# Function to analyze a single wallet
def analyze_wallet(address, timeframe, minimum_wallet_capital, minimum_avg_holding_period, minimum_win_rate, minimum_total_pnl):
    if not check_wallet_capital(address, minimum_wallet_capital):
        print(f"Wallet {address} excluded due to insufficient capital.")
        return None

    transactions = fetch_transaction_history(address)
    if not transactions:
        print(f"No transactions found for wallet: {address}")
        return {
            "address": address,
            "total_pnl": 0,
            "realized_pnl": 0,
            "unrealized_pnl": 0,
            "win_rate": 0,
            "buy_sell_dates": []  # New field to store buy/sell dates and times
        }

    total_pnl = 0
    realized_pnl = 0
    unrealized_pnl = 0
    profitable_trades = 0
    total_trades = 0
    buy_sell_dates = []  # List to store dates and times of buy/sell transactions

    bought_assets = {}  # Track assets purchased in the timeframe

    for tx in transactions:
        if tx.get("err") is not None:
            print(f"Skipping transaction {tx['signature']} due to errors.")
            continue

        details = fetch_transaction_details(tx['signature'])
        if not details:
            print(f"Error fetching details for transaction {tx['signature']}.")
            continue

        timestamp = details['blockTime']
        transaction_datetime = timestamp_to_datetime(int(timestamp))

        # Skip pre-timeframe transactions
        if not is_within_timeframe(timestamp, timeframe):
            continue

        is_buy = "buy_condition" in details  # Replace with actual logic to detect buy
        is_sell = "sell_condition" in details  # Replace with actual logic to detect sell
        is_transfer = "transfer_condition" in details  # Replace with logic to detect transfers

        # Handle buy transactions
        if is_buy:
            price = get_token_price("SOL")  # Replace with actual token price fetching logic
            amount = 10  # Replace with actual transaction amount
            unrealized_pnl -= amount * price
            bought_assets[details["token_id"]] = {"price": price, "amount": amount, "timestamp": timestamp}
            buy_sell_dates.append({'transaction': 'buy', 'datetime': transaction_datetime})

        # Handle sell transactions
        elif is_sell:
            price = get_token_price("SOL")  # Replace with actual token price fetching logic
            amount = 10  # Replace with actual transaction amount
            realized_pnl += amount * price
            profitable_trades += 1 if amount * price > 0 else 0
            buy_sell_dates.append({'transaction': 'sell', 'datetime': transaction_datetime})

        # Handle transfers (if applicable)
        elif is_transfer:
            token_id = details.get("token_id")
            if token_id in bought_assets:
                asset = bought_assets.pop(token_id)
                price = get_token_price("SOL")  # Replace with the price at transfer time
                realized_pnl += asset["amount"] * price
                buy_sell_dates.append({'transaction': 'transfer_sell', 'datetime': transaction_datetime})

        total_trades += 1
        time.sleep(random.uniform(0.2, 0.4))  # Randomize delay for backoff

    total_pnl = realized_pnl + unrealized_pnl
    win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0

    # Exclude based on win rate and total PNL
    if win_rate < minimum_win_rate:
        print(f"Wallet {address} excluded due to low win rate.")
        return None

    avg_holding_period = calculate_avg_holding_period(buy_sell_dates)
    if avg_holding_period < minimum_avg_holding_period:
        print(f"Wallet {address} excluded due to short average holding period.")
        return None

    if total_pnl < minimum_total_pnl:
        print(f"Wallet {address} excluded due to low total PNL.")
        return None

    return {
        "address": address,
        "total_pnl": total_pnl,
        "realized_pnl": realized_pnl,
        "unrealized_pnl": unrealized_pnl,
        "win_rate": win_rate,
        "buy_sell_dates": buy_sell_dates
    }

# Function to check if the transaction is within the specified timeframe
def is_within_timeframe(tx_timestamp, timeframe):
    current_time = datetime.now()
    delta = current_time - datetime.fromtimestamp(tx_timestamp)

    if timeframe == '1':
        return delta.days <= 30
    elif timeframe == '3':
        return delta.days <= 90
    elif timeframe == '6':
        return delta.days <= 180
    elif timeframe == '12':
        return delta.days <= 365
    else:
        return True  # No filtering if 'overall'

# Import wallet addresses from CSV
def import_wallet_addresses(file_path):
    wallet_addresses = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            wallet_addresses.append(row[0])  # Assuming wallet addresses are in the first column
    print(f"Successfully imported {len(wallet_addresses)} wallet addresses.")
    return wallet_addresses

# Export results to CSV
def export_to_csv(analysis_results):
    valid_results = [result for result in analysis_results if result is not None]

    if not valid_results:
        print("No valid results to export.")
        return

    fieldnames = ["address", "total_pnl", "realized_pnl", "unrealized_pnl", "win_rate", "buy_sell_dates"]
    
    try:
        with open('analysis_results.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for result in valid_results:
                writer.writerow(result)
        print(f"Results successfully exported: {len(valid_results)} wallets.")
    except Exception as e:
        print(f"Error exporting results: {e}")

# Main function
def main():
    print("Welcome to Solana Wallet Analyzer Bot!")
    wallet_addresses = []
    analysis_results = []

    while True:
        print("\nMenu:")
        print("1. Import wallet addresses from CSV")
        print("2. Analyze wallets")
        print("3. Export results to CSV")
        print("4. Quit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            file_path = input("Enter the CSV file path: ")
            wallet_addresses = import_wallet_addresses(file_path)

        elif choice == '2':
            if not wallet_addresses:
                print("No wallet addresses imported. Please import first.")
                continue
            timeframe = input("Enter analysis timeframe (1, 3, 6, 12 months, or overall): ")
            minimum_wallet_capital = float(input("Enter minimum wallet capital in USD: "))
            minimum_avg_holding_period = float(input("Enter minimum average holding period in minutes: "))
            minimum_win_rate = float(input("Enter minimum win rate in percentage: "))
            minimum_total_pnl = float(input("Enter minimum total PNL in USD: "))
            analysis_results = [
                analyze_wallet(addr, timeframe, minimum_wallet_capital, minimum_avg_holding_period, minimum_win_rate, minimum_total_pnl) 
                for addr in wallet_addresses
            ]
            print("Analysis complete!")

        elif choice == '3':
            if not analysis_results:
                print("No analysis results available. Please run an analysis first.")
                continue
            export_to_csv(analysis_results)

        elif choice == '4':
            print("Thank you for using Solana Wallet Analyzer Bot. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
