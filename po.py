import asyncio
import aiohttp
from mnemonic import Mnemonic
from hdwallet import HDWallet
import hashlib
import base58
import time

# Параметры настройки
MAX_CONCURRENT_REQUESTS = 10  # Максимальное количество одновременных запросов
RETRY_LIMIT = 5                # Количество повторных попыток при неудаче
BACKOFF_FACTOR = 0.5           # Фактор экспоненциальной задержки

# Семафор для ограничения количества одновременных запросов
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def fetch_balance(session, url):
    """Асинхронный запрос баланса по API с обработкой повторных попыток."""
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            async with semaphore:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status in {429, 500, 502, 503, 504}:
                        # 429 Too Many Requests или серверные ошибки
                        retries += 1
                        wait_time = BACKOFF_FACTOR * (2 ** retries)
                        print(f"Получен статус {response.status}. Повторная попытка через {wait_time} секунд...")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"Ошибка при запросе {url}: статус {response.status}")
                        return None
        except aiohttp.ClientError as e:
            retries += 1
            wait_time = BACKOFF_FACTOR * (2 ** retries)
            print(f"Ошибка клиента при запросе {url}: {e}. Повторная попытка через {wait_time} секунд...")
            await asyncio.sleep(wait_time)
    print(f"Не удалось получить данные для {url} после {RETRY_LIMIT} попыток.")
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
        try:
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
        except Exception as e:
            print(f"Ошибка при деривации пути {path}: {e}")
    return addresses

async def process_mnemonics():
    """Бесконечный цикл для генерации мнемоников и проверки адресов."""
    while True:
        try:
            # Генерация случайной мнемоники
            mnemonic = Mnemonic("english")
            words = mnemonic.generate(strength=256)
            print(f"\nСгенерирована мнемоника: {words}")

            # Пути для генерации адресов
            derivation_paths = [
                "m/44'/0'/0'/0/0",
                "m/44'/0'/0'/0/1",
                "m/0'/0'/0'",
                "m/0/0",
            ]

            # Генерация адресов
            addresses = derive_addresses(words, derivation_paths)
            print(f"Сгенерированные адреса: {addresses}")

            # Проверка балансов адресов
            balances = await check_balances(addresses)
            for addr, data in balances.items():
                try:
                    balance = int(data.get("balance", 0))  # Преобразование в целое число
                    txs = int(data.get("txs", 0))          # Преобразование в целое число
                except ValueError:
                    print(f"Неверный формат данных для адреса {addr}. Пропуск...")
                    continue

                print(f"Адрес: {addr}, Баланс: {balance}, Транзакции: {txs}")

                # Сохранение данных о найденных адресах
                if balance > 0 or txs > 0:
                    with open("found_addresses.txt", "a") as f:
                        f.write(f"Мнемоника: {words}\n")
                        f.write(f"Адрес: {addr}, Баланс: {balance}, Транзакции: {txs}\n")
                        f.write("\n")
        except Exception as e:
            print(f"Необработанная ошибка: {e}. Продолжаем работу...")
            await asyncio.sleep(1)  # Короткая задержка перед продолжением

if __name__ == "__main__":
    try:
        asyncio.run(process_mnemonics())
    except KeyboardInterrupt:
        print("\nСкрипт остановлен пользователем.")