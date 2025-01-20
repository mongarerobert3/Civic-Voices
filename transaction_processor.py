from datetime import datetime
from transaction_fetcher import TransactionFetcher

class TransactionProcessor:
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
						# Assume we're working with lamports (common in Solana) and convert to SOL
						amount_in_sol = amount["lamports"] / 10**9  # Convert lamports to SOL
				else:
						amount_in_sol = amount  # If it's already in SOL, use it directly

				# Process based on transaction type
				if transaction_type == "buy":
						# For buy transactions, process differently, perhaps adding the amount to a balance
						processed_tx["type"] = "buy"
						processed_tx["amount"] = amount_in_sol
						processed_tx["fees"] = fees
						processed_tx["net_amount"] = amount_in_sol - fees  # Net amount after fees
				elif transaction_type == "sell":
						# For sell transactions, track the amount sold and any associated fees
						processed_tx["type"] = "sell"
						processed_tx["amount"] = amount_in_sol
						processed_tx["fees"] = fees
						processed_tx["net_amount"] = amount_in_sol - fees  # Net amount after fees
				else:
						# Handle other transaction types (e.g., transfer, stake, etc.)
						processed_tx["type"] = "other"
						processed_tx["amount"] = amount_in_sol

				# Add signature for tracking
				processed_tx["id"] = signature

				# Add timestamp if available
				if timestamp:
						processed_tx["timestamp"] = timestamp

				# Additional processing can be added here (e.g., adjusting for token prices, PnL calculation)
				
				return processed_tx

		@staticmethod
		def filter_and_process_transactions(transactions, timeframe):
				"""
				Filters and processes transactions based on the timeframe.

				Parameters:
						transactions (list): A list of transaction dictionaries.
						timeframe (tuple): A tuple containing start and end timestamps for filtering.

				Returns:
						list: A list of processed buy/sell transactions within the specified timeframe.
				"""
				filtered_transactions = []

				for tx in transactions:
						# Skip transactions with errors
						if tx.get("err"):
								print(f"Transaction {tx['signature']} skipped due to error: {tx['err']}")
								continue

						# Fetch transaction details (assuming a method exists to do this)
						details = fetch_transaction_details(tx["signature"])  # This should be defined in your context
						if not details:
								print(f"Transaction {tx['signature']} skipped due to missing details.")
								continue

						# Check if transaction is within the timeframe
						block_time = datetime.fromtimestamp(details["blockTime"])
						if not TransactionProcessor.is_within_timeframe(block_time, timeframe):
								continue

						# Determine transaction type (replace with actual conditions)
						is_buy = "buy_condition" in details  # Replace with real condition for "buy"
						is_sell = "sell_condition" in details  # Replace with real condition for "sell"

						if is_buy or is_sell:
								transaction_type = "buy" if is_buy else "sell"
								processed_transaction = TransactionProcessor.process_transaction({
										"signature": tx["signature"],
										"amount": details.get("amount", 0),  # Assuming amount exists in details
										"type": transaction_type,
										"timestamp": details["blockTime"]
								})
								filtered_transactions.append(processed_transaction)
						else:
								print(f"Transaction {tx['signature']} skipped (not buy or sell).")
				
				print(f"Filtered and processed {len(filtered_transactions)} buy/sell transactions.")
				return filtered_transactions


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
