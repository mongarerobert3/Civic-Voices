import time
import json
import requests
import logging
from decouple import config


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class APIClient:
    def __init__(self, use_helius=False):
        self.HELIUS_RPC_URL = config("HELIUS_RPC_URL")
        self.SOLANA_RPC_URL = config("SOLANA_RPC_URL")
        self.TOKEN_PROGRAM_ID = config("TOKEN_PROGRAM_ID")
        self.use_helius = use_helius
        self.API_ENDPOINT = self.HELIUS_RPC_URL if self.use_helius else self.SOLANA_RPC_URL
        self.last_response = None

    def post_request(self, method, params):
        headers = {"Content-Type": "application/json"}
        data = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        retries, backoff_time = 2, 1

        for attempt in range(retries):
            try:
                response = requests.post(self.API_ENDPOINT, headers=headers, json=data)
                self.last_response = response.json()
                if response.status_code == 429:  # Rate-limiting
                    print(f"Rate limit exceeded (attempt {attempt+1}/{retries}). Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    backoff_time *= 2
                elif response.status_code == 200:
                    return response.json()
                else:
                    print(f"Unexpected error: {response.status_code}, {json.dumps(self.last_response, indent=2)}")
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt+1}/{retries}): {e}")
                time.sleep(backoff_time)
                backoff_time *= 2

        print("Exceeded retry limit for this request.")
        return None

    def get_token_accounts_by_owner(self, wallet_address):
        params = [
            wallet_address,
            {"programId": self.TOKEN_PROGRAM_ID},
            {"encoding": "jsonParsed"}
        ]
        result = self.post_request("getTokenAccountsByOwner", params)
        if result and 'result' in result:
            return [account['pubkey'] for account in result['result']['value']]
        print("Failed to fetch token accounts.")
        return None
