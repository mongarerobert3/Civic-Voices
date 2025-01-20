from datetime import datetime
from transaction_fetcher import TransactionFetcher

class TransactionProcessor:
    def __init__(self):
        self.transaction_fetcher = TransactionFetcher()

    @staticmethod
    def filter_transactions(transactions):
        """
        Filters transactions to include only buy and sell types.

        Parameters:
                transactions (list): A list of transaction dictionaries.

        Returns:
                list: A list of filtered buy/sell transactions.
        """
        buy_sell_transactions = [t for t in transactions if t["type"] in ["buy", "sell"]]
        return buy_sell_transactions

    @staticmethod
    def process_transaction(transaction):
        """
        Processes a single transaction, calculating important details like value, type, and fees.

        Parameters:
                transaction (dict): The transaction dictionary to process.

        Returns:
                dict: A dictionary with processed transaction data, including transaction type, amount, fees, and tokens.
        """
        processed_tx = {}

        # Extract basic fields
        signature = transaction.get("signature")
        amount = transaction.get("amount")  # The transaction amount
        transaction_type = transaction.get("type")  # Can be 'buy', 'sell', or other
        fees = transaction.get("fee", 0)  # Transaction fee, default to 0 if not available
        timestamp = transaction.get("timestamp")  # Time of the transaction (if available)

        # Convert amount if needed (e.g., lamports to SOL if applicable)
        if "lamports" in amount:
            amount_in_sol = amount["lamports"] / 10**9  # Convert lamports to SOL
        else:
            amount_in_sol = amount  # If it's already in SOL, use it directly

        # Process based on transaction type
        if transaction_type == "buy":
            processed_tx["type"] = "buy"
            processed_tx["amount"] = amount_in_sol
            processed_tx["fees"] = fees
            processed_tx["net_amount"] = amount_in_sol - fees  # Net amount after fees
        elif transaction_type == "sell":
            processed_tx["type"] = "sell"
            processed_tx["amount"] = amount_in_sol
            processed_tx["fees"] = fees
            processed_tx["net_amount"] = amount_in_sol - fees  # Net amount after fees
        else:
            processed_tx["type"] = "other"
            processed_tx["amount"] = amount_in_sol

        # Add signature for tracking
        processed_tx["id"] = signature

        # Add timestamp if available
        if timestamp:
            processed_tx["timestamp"] = timestamp

        return processed_tx

    @staticmethod
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
