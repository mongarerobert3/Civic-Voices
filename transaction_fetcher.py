from api_client import APIClient

class TransactionFetcher:
    def __init__(self, batch_size=2):
        self.client = APIClient()
        self.batch_size = batch_size

    def fetch_transaction_history(self, wallet_address):
        """
        Fetches the transaction history for a given wallet address in batches.

        Parameters:
            wallet_address (str): The wallet address to fetch transactions for.

        Returns:
            list: A list of all fetched transactions.
        """
        all_transactions = []
        before_signature = None
        
        while True:
            # Prepare parameters for the API request
            params = [wallet_address, {"limit": self.batch_size}]
            if before_signature:
                params[1]["before"] = before_signature

            # Fetch transactions
            result = self.client.post_request("getSignaturesForAddress", params)
            if not result or "result" not in result:
                print(f"Error fetching transactions for {wallet_address}.")
                break
            
            transactions = result["result"]
            if not transactions:
                break  # No more transactions to fetch

            all_transactions.extend(transactions)
            before_signature = transactions[-1]["signature"]

            if len(transactions) < self.batch_size:
                break  # Reached the end of available transactions

        print(f"Fetched {len(all_transactions)} transactions for {wallet_address}.")
        return all_transactions

    def fetch_transaction_details(self, transaction_id):
        """
        Fetches detailed information about a specific transaction.

        Parameters:
            transaction_id (str): The ID of the transaction to fetch details for.

        Returns:
            dict or None: The details of the transaction if successful, None otherwise.
        """
        result = self.client.post_request(f"getTransaction/{transaction_id}", {"encoding": "jsonParsed"})
        if not result:
            return None
        return result.get("result", None)

    def fetch_wallet_balance(self, address):
        """
        Fetches the balance of a specified wallet address in SOL.

        Parameters:
            address (str): The wallet address to fetch the balance for.

        Returns:
            float: The balance in SOL.
        """
        result = self.client.post_request("getBalance", [address])
        
        if result and "result" in result:
            sol_balance = result["result"]["value"] / 10**9  # Convert lamports to SOL
            return sol_balance
        else:
            print(f"Error fetching balance for {address}")
            return 0.0
