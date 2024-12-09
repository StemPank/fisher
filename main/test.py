import psycopg2
from psycopg2 import Error
import setting

try:
    connection = psycopg2.connect(user = setting.POSTGRES_USER,
                                password=setting.POSTGRES_PASSWORD,
                                host=setting.POSTGRES_HOST,
                                port=setting.POSTGRES_PORT,
                                database=setting.POSTGRES_DB)
    print('Подключение успешно')
except Error as e:
    print(f'Ошибка подключение: {e}')
    

from binance.spot import Spot as Client

spot_client = Client(base_url="https://testnet.binance.vision")

print(spot_client.klines("BTCUSDT", "1m"))

