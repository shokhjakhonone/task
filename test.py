import os
import secrets
import hashlib
import requests
from eth_keys import keys
from eth_utils import keccak
import concurrent.futures
import json

# Define Ethereum, ETC, and BNB RPC endpoints
ETH_RPC_ENDPOINTS = ["https://eth-pokt.nodies.app", "https://rpc.ankr.com/eth", "https://eth.meowrpc.com", "https://rpc.mevblocker.io"]
ETC_RPC_ENDPOINTS = ["https://etc.etcdesktop.com", "https://etc.rivet.link"]
BNB_RPC_ENDPOINTS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed1.ninicoin.io/"]

TOKEN_CONTRACT_ADDRESSES = {
    "Shiba": "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce",
    "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec7",  # Tether USDT
    "Pepe": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
    "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "Toncoin": "0x582d872a1b094fc48f5de31d3b73f2d9be47def1",
    "WBTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
    "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "Cronos": "0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b",
    "ARB": "0xb50721bcf8d664c30412cfbc6cf7a15145234ad1",
    "BONK": "0x1151cb3d861920e07a38e03eead12c32178567f6",
    "FLOKI": "0xcf0c122c6b73ff809c693db761e7baebe62b6a2e",
    "Polygon": "0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0",
    "Gala": "0xd1d2eb1b1e90b638588728b4130137d262c87cae",
    "Gate": "0xe66747a101bff2dba3697199dcce5b743b454759",
    "Quant": "0x4a220e6096b25eadb88358cb44068a3248254675",
    "JasMyCoin": "0x7420b4b9a0110cdc71fb720908340c03f9bc03ec",
    "Lido DAO": "0x5a98fcbea516cf06857215779fd812ca3bef1b32",
    "Ondo": "0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3",
    "Mantra": "0x3593d125a4f7849a1b059e64f4517a86dd60c95d",
    "PayPal USD": "0x6c3ea9036406852006290770bedfcaba0e23a0e8",
    "Worldcoin": "0x163f8c2467924be0ae7b5347228cabf260318753",
    "Axie Infinity": "0xbb0e17ef65f82ab018d8edd776e8dd940327b28b",
    "Tokenize Xchange": "0x667102bd3413bfeaa3dffb48fa8288819e480a88",
    "Tether Gold": "0x68749665ff8d2d112fa859aa293f07a622782f38",
    "ApeCoin": "0x4d224452801aced8b2f0aebe155379bb5d594381",
    "ENS": "0xc18360217d8f7ab5e7c516566761ea12ce7f9d72",
    "PancakeSwap": "0x152649ea73beab28c5b49b26eb48f7ead6d4c898",
    "Decentraland": "0x0f5d2fb29fb7d3cfee444a200298f468908cc942",
    "Lido Staked Ether": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
    "Wrapped stETH": "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",

    
}

# Define color functions for terminal output
def purple(text):
    os.system(""); faded = ""
    for line in text.splitlines():
        red = 128
        for character in line:
            if red < 255:
                red += 5
            faded += (f"\033[38;2;{red};0;128m{character}\033[0m")
        faded += "\n"
    return faded

def orange(text):
    os.system(""); faded = ""
    for line in text.splitlines():
        orange = 255
        for character in line:
            orange -= 5
            if orange < 0:
                orange = 0
            faded += (f"\033[38;2;{orange};165;0m{character}\033[0m")
        faded += "\n"
    return faded

def water(text):
    os.system(""); faded = ""
    green = 10
    for line in text.splitlines():
        faded += (f"\033[38;2;0;{green};255m{line}\033[0m\n")
        if not green == 255:
            green += 15
            if green > 255:
                green = 255
    return faded

# Function to send JSON-RPC request to get balance for ETH, ETC, or BNB
def get_balance(address, rpc_url):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    try:
        response = requests.post(rpc_url, json=payload)
        if response.status_code == 200:
            result = response.json().get("result")
            if result and isinstance(result, str):
                balance = int(result, 16) / (10 ** 18)  # Convert from wei to token units
                return balance
            else:
                print(f"Unexpected response for address {address}: {result}")
        else:
            print(f"Error getting balance for address {address}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending balance request: {str(e)}")
    return 0

# Function to get token balance
def get_token_balance(address, token_contract, rpc_url):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": token_contract,
                "data": "0x70a08231000000000000000000000000" + address[2:]  # balanceOf(address)
            },
            "latest"
        ],
        "id": 1
    }
    try:
        response = requests.post(rpc_url, json=payload)
        if response.status_code == 200:
            result = response.json().get("result")
            if result and isinstance(result, str):
                balance = int(result, 16) / (10 ** 18)  # Convert from wei to token units
                return balance
            else:
                print(f"Unexpected response for address {address}: {result}")
        else:
            print(f"Error getting token balance for address {address}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending token balance request: {str(e)}")
    return 0

# Generate private key
def generate_private_key():
    return secrets.token_bytes(32)  # 32 bytes = 256 bits

# Convert private key to public key and address using eth_keys library
def private_key_to_eth_address(private_key_bytes):
    private_key = keys.PrivateKey(private_key_bytes)
    public_key = private_key.public_key
    eth_address = public_key.to_checksum_address()  # Derives the correct EIP-55 address
    return eth_address, private_key.to_hex()

# Function to generate and check balances for ETH, ETC, and BNB
def generate_and_check_eth_etc_bnb(derivation_index):
    # Generate private keys for ETH, ETC, and BNB
    private_key_bytes_eth = generate_private_key()
    private_key_bytes_etc = generate_private_key()
    private_key_bytes_bnb = generate_private_key()

    # Generate Ethereum address
    eth_address, private_key_hex_eth = private_key_to_eth_address(private_key_bytes_eth)
    etc_address, private_key_hex_etc = private_key_to_eth_address(private_key_bytes_etc)
    bnb_address, private_key_hex_bnb = private_key_to_eth_address(private_key_bytes_bnb)  # Same method for address generation

    # Check balances from one of the endpoints
    eth_balance = next((get_balance(eth_address, rpc) for rpc in ETH_RPC_ENDPOINTS if (eth_balance := get_balance(eth_address, rpc)) > 0), 0)
    etc_balance = next((get_balance(etc_address, rpc) for rpc in ETC_RPC_ENDPOINTS if (etc_balance := get_balance(etc_address, rpc)) > 0), 0)
    bnb_balance = next((get_balance(bnb_address, rpc) for rpc in BNB_RPC_ENDPOINTS if (bnb_balance := get_balance(bnb_address, rpc)) > 0), 0)

    # Get token balances for each specified token
    token_balances = {token: next((get_token_balance(eth_address, contract, rpc) for rpc in ETH_RPC_ENDPOINTS), 0) for token, contract in TOKEN_CONTRACT_ADDRESSES.items()}

    return eth_address, etc_address, bnb_address, eth_balance, etc_balance, bnb_balance, token_balances, private_key_hex_eth, private_key_hex_etc, private_key_hex_bnb, derivation_index

# Save the results to a file
def save_to_file_eth_etc_bnb(eth_address, etc_address, bnb_address, eth_balance, etc_balance, bnb_balance, token_balances, private_key_hex_eth, private_key_hex_etc, private_key_hex_bnb, derivation_index):
    with open('foundmoney_eth_etc_bnb.txt', 'a') as file:
        file.write(f"Derivation Index: {derivation_index}\n")
        file.write(f"Ethereum Address: {eth_address}\n")
        file.write(f"Ethereum Classic Address: {etc_address}\n")
        file.write(f"BNB Address: {bnb_address}\n")
        file.write(f"ETH Private Key: {private_key_hex_eth}\n")
        file.write(f"ETC Private Key: {private_key_hex_etc}\n")
        file.write(f"BNB Private Key: {private_key_hex_bnb}\n")
        file.write(f"ETH Balance: {eth_balance} ETH\n")
        file.write(f"ETC Balance: {etc_balance} ETC\n")
        file.write(f"BNB Balance: {bnb_balance} BNB\n")
        for token, balance in token_balances.items():
            file.write(f"{token} Balance: {balance} Tokens\n")
        file.write("=" * 40 + "\n")

# Main function for generating and checking ETH, ETC, and BNB addresses
def main_eth_etc_bnb():
    global start_bits, end_bits, eth_derivations, etc_derivations, bnb_derivations
    start_bits = int(input(purple("Enter the start bit range (e.g., 128): ")))
    end_bits = int(input(purple("Enter the end bit range (e.g., 256): ")))
    eth_derivations = int(input(purple("Enter the number of derivations to check for ETH: ")))
    etc_derivations = int(input(purple("Enter the number of derivations to check for ETC: ")))
    bnb_derivations = int(input(purple("Enter the number of derivations to check for BNB: ")))

    found = False
    max_workers = 8  # Adjust based on system capability

    print(water(f"\nGenerating and checking keys in parallel with {max_workers} workers..."))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        derivation_indices = range(max(eth_derivations, etc_derivations, bnb_derivations))
        while not found:
            futures = [executor.submit(generate_and_check_eth_etc_bnb, i) for i in derivation_indices]

            for future in concurrent.futures.as_completed(futures):
                eth_address, etc_address, bnb_address, eth_balance, etc_balance, bnb_balance, token_balances, private_key_hex_eth, private_key_hex_etc, private_key_hex_bnb, derivation_index = future.result()

                print(orange(f"Derivation Index: {derivation_index}"))
                print(orange(f"Ethereum Address: {eth_address}"))
                print(orange(f"Ethereum Classic Address: {etc_address}"))
                print(orange(f"BNB Address: {bnb_address}"))
                print(orange(f"ETH Private Key: {private_key_hex_eth}"))
                print(orange(f"ETC Private Key: {private_key_hex_etc}"))
                print(orange(f"BNB Private Key: {private_key_hex_bnb}"))
                print(orange(f"ETH Balance: {eth_balance} ETH"))
                print(orange(f"ETC Balance: {etc_balance} ETC"))
                print(orange(f"BNB Balance: {bnb_balance} BNB"))

                for token, balance in token_balances.items():
                    print(orange(f"{token} Balance: {balance} Tokens"))

                if eth_balance > 0 or etc_balance > 0 or bnb_balance > 0 or any(balance > 0 for balance in token_balances.values()):
                    save_to_file_eth_etc_bnb(eth_address, etc_address, bnb_address, eth_balance, etc_balance, bnb_balance, token_balances, private_key_hex_eth, private_key_hex_etc, private_key_hex_bnb, derivation_index)
                    found = True
                    break

if __name__ == '__main__':
    main_eth_etc_bnb()
