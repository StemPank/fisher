from binance.spot import Spot as Client

def klines(symbol: str, interval: str, **kwargs):
    """
    Arguments:
        symbol (str): торговая пара
        interval (str): интервал kline, например 1s, 1m, 5m, 1h, 1d и т. д.
    Keyword Arguments:
        limit (int, необязательно): ограничение результатов. По умолчанию 500; макс. 1000.
        startTime (int, необязательно): временная метка в мс для получения агрегированных сделок от INCLUSIVE.
        endTime (int, необязательно): временная метка в мс для получения агрегированных сделок до INCLUSIVE.
        timeZone (str, необязательно): по умолчанию: 0 (UTC)
    """
    return Client(base_url="https://api1.binance.com").klines(symbol, interval, **kwargs)