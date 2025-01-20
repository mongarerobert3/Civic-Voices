import time
import json
import requests
from decouple import config

class APIClient:
    def __init__(self, use_helius=False):
        # Load API endpoints from environment variables
        self.HELIUS_RPC_URL = config("HELIUS_RPC_URL")
        self.HELIUS_PARSE_URL = config("HELIUS_PARSE_URL")
        self.HELIUS_TRANSACTION_PARSE_URL = config("HELIUS_TRANSACTION_PARSE_URL")
        self.SOLANA_RPC_URL = config("SOLANA_RPC_URL")
        self.TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # SPL Token Program ID
        self.use_helius = use_helius
        self.API_ENDPOINT = self.HELIUS_RPC_URL if self.use_helius else self.SOLANA_RPC_URL

    def post_request(self, method, params):
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
            try:
                response = requests.post(self.API_ENDPOINT, headers=headers, json=data)
                result = response.json()

                # Store the last response for debugging
                self.last_response = response.json()

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

            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt+1}/{retries}): {e}")
                time.sleep(backoff_time)  # Delay on error
                backoff_time = min(backoff_time * 2, 32)  # Max 32 seconds delay before retrying

        print("Exceeded retry limit for this request. Skipping transaction.")
        return None

    def get_token_accounts_by_owner(self, wallet_address):
        """
        Fetches all token accounts related to a specific wallet owner.
        
        Parameters:
            owner_public_key (str): The public key of the wallet owner.
        
        Returns:
            list: A list of token accounts, or None if the request fails.
        """
        params = [
            wallet_address,  # The wallet address
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},  # Token program ID
            {"encoding": "jsonParsed"}  # Optional encoding
        ]
        
        result = self.post_request("getTokenAccountsByOwner", params)
        
        if result and 'result' in result:
            #print(f"Found {len(result['result'])} token accounts for owner {wallet_address}.")
            #return [account['pubkey'] for account in result['result']]  # Return only account public keys
            print(f"Raw API result: {result['result']}")

        print("Failed to fetch token accounts.")
        return None
