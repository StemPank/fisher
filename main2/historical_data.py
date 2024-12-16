from binance.spot import Spot as Client
from multiprocessing import Queue
import pandas as pd

def historical_data(queue_kline: Queue, queue_kline_gui: Queue, shared_data):
    coin = None
    print("Запуск historical_data")
    while True: 
        command = shared_data.get("command")
        if command and command["type"] == "change_coin" and command["coin"] != coin:
            coin = command["coin"]
            print(f"Загрузка исторических данных {coin}")
            spot_client = Client(base_url="https://api1.binance.com")
            klines = spot_client.klines(coin, "1m", limit=300)
                
            for kline in klines:
                data = {
                    "s" : coin,
                    "t" : kline[0],
                    "o" : float(kline[1]),
                    "h" : float(kline[2]),
                    "l" : float(kline[3]),
                    "c" : float(kline[4]),
                }
                
                queue_kline.put(data)
                queue_kline_gui.put(data)


def historical_data_copy():
    spot_client = Client(base_url="https://api1.binance.com")
    klines = spot_client.klines('BTCUSDT', "1m", limit=300)
    pd.set_option('display.max_rows', None)
    all_data = pd.DataFrame(klines, columns=["t", "o", "h", "l", "c", "v", "T", "q", "n", "V", "Q", "B"]) 
    print(all_data)
if __name__ == "__main__":
    historical_data_copy()
