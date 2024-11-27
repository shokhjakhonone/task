import asyncio
import aiohttp
from mnemonic import Mnemonic
from hdwallet import HDWallet
import hashlib
import base58


async def fetch_balance(session, url):
    """Асинхронный запрос баланса по API."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching {url}: {response.status}")
                return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


async def check_balances(addresses):
    """Асинхронная проверка баланса списка адресов."""
    results = {}
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_balance(session, f'https://btcbook.guarda.co/api/v2/address/{addr}')
            for addr in addresses
        ]
        responses = await asyncio.gather(*tasks)
        for address, response in zip(addresses, responses):
            if response:
                results[address] = response
    return results


def derive_addresses(words, derivation_paths):
    """Генерация адресов из мнемоников по указанным путям."""
    hdwallet = HDWallet().from_mnemonic(words)
    addresses = []
    for path in derivation_paths:
        hdwallet.from_path(path=path)
        compressed_pub_key = hdwallet.public_key(compressed=True)
        uncompressed_pub_key = '04' + hdwallet.public_key(compressed=False)
        
        # Генерация сжатого адреса
        compressed_addr_bytes = hashlib.new(
            'ripemd160', hashlib.sha256(bytes.fromhex(compressed_pub_key)).digest()
        ).digest()
        compressed_addr = base58.b58encode_check(b'\x00' + compressed_addr_bytes).decode()
        addresses.append(compressed_addr)
        
        # Генерация несжатого адреса
        uncompressed_addr_bytes = hashlib.new(
            'ripemd160', hashlib.sha256(bytes.fromhex(uncompressed_pub_key)).digest()
        ).digest()
        uncompressed_addr = base58.b58encode_check(b'\x00' + uncompressed_addr_bytes).decode()
        addresses.append(uncompressed_addr)
    return addresses


async def process_mnemonics():
    """Бесконечный цикл для генерации мнемоников и проверки адресов."""
    while True:
        # Генерация случайной мнемоники
        mnemonic = Mnemonic("english")
        words = mnemonic.generate(strength=256)
        print(f"Generated mnemonic: {words}")

        # Пути для генерации адресов
        derivation_paths = [
            "m/44'/0'/0'/0/0",
            "m/44'/0'/0'/0/1",
            "m/0'/0'/0'",
            "m/0/0",
        ]

        # Генерация адресов
        addresses = derive_addresses(words, derivation_paths)
        print(f"Derived addresses: {addresses}")

        # Проверка балансов адресов
        balances = await check_balances(addresses)
        for addr, data in balances.items():
            balance = int(data.get("balance", 0))  # Преобразование в целое число
            txs = int(data.get("txs", 0))          # Преобразование в целое число
            print(f"Address: {addr}, Balance: {balance}, Transactions: {txs}")

            # Сохранение данных о найденных адресах
            if balance > 0 or txs > 0:
                with open("found_addresses.txt", "a") as f:
                    f.write(f"Mnemonic: {words}\n")
                    f.write(f"Address: {addr}, Balance: {balance}, Transactions: {txs}\n")
                    f.write("\n")


if __name__ == "__main__":
    asyncio.run(process_mnemonics())