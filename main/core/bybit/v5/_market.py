from pybit.unified_trading import HTTP

BYBIT_API_KEY = "api_key"
BYBIT_API_SECRET = "api_secret"
TESTNET = True  # True означает, что ваши ключи API были сгенерированы на testnet.bybit.com

class Market:
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = None,):
        self.instance = HTTP(api_key=api_key, api_secret=api_secret, testnet=testnet, log_requests=True )

    def klines(self, symbol: str, interval: str, **kwargs):
        """
        Arguments:
            symbol (str): торговая пара
            interval (str): интервал kline в минутах, например 1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, M, W
        Keyword Arguments:
            category (str, необязательно): тип продукта. spot, linear, inverse. Когда не передано, использовать по умолчанию linear
            limit (int, необязательно): ограничение результатов. По умолчанию 200; макс. 1000.
            startTime (int, необязательно): временная метка в мс 
            endTime (int, необязательно): временная метка в мс 
        """
        kline_data = self.instance.get_kline(symbol=symbol, interval=interval, **kwargs)["result"]
        return kline_data["list"]

        # Getting 0 element from list
        data_list = kline_data["list"][0]

        print(f"Open price: {data_list[1]}")
        print(f"High price: {data_list[2]}")
        print(f"Low price: {data_list[3]}")
        print(f"Close price: {data_list[4]}")