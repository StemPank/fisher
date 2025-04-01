LIST_PROVIDERS = ["binance", "bybit"]

LIST_LANGUAGE = ["English", "Русский"]

LIST_OF_AVAILABLE_BASE_ENDPOINTS = {
    "binance": ["test", 
                "https://api.binance.com", 
                "https://api-gcp.binance.com", 
                "https://api1.binance.com", 
                "https://api2.binance.com", 
                "https://api3.binance.com", 
                "https://api4.binance.com"
                ],
    "bybit": ["test",
              "https://api.bybit.com",
            #   "https://api.bytick.com"
            ]
}

LIST_PAIR = ["BTCUSDT", "ATRUSDT", "ETHUSDT"]
LIST_INTERVALS = {
    "binance" : ["1s", "1m", "5m", "15m", "1h", "2h", "1d", "1W", "1M"],
    'bybit' : ["1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"]
}