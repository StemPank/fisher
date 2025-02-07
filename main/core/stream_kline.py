import os, sys, importlib
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
from pybit.unified_trading import WebSocketTrading, WebSocket

import core.table_for_agent as table_for_agent

class StreamKline():
    def __init__(self, agent_name, setting_data, key, coin=None, interval=None, queue=None):
        
        self.agent_name = agent_name
        self.setting_data = setting_data
        self.coin = coin
        self.interval = interval
        self.queue = queue
        
        """
            hasattr(self, name): проверяет, есть ли у объекта метод с именем name.
            callable(getattr(self, name)): проверяет, является ли он вызываемым (т.е. функцией).
            getattr(self, name)(): если метод найден, он вызывается.
        """
        if hasattr(self, self.setting_data) and callable(getattr(self, self.setting_data)):
            # Вызываем метор с именем ↓,   передаем аргументы ↓
            getattr(self, self.setting_data)(key) 
        else:
            print(f"Метод '{self, self.setting_data}' не найден.")

    

    def binance(self, key):
        """
            Подключение к Websocket binance 

            :key (str) - команда "start", "stop"
        """
        self.my_client = SpotWebsocketStreamClient(on_message=self.message_handler_binance, 
                                        on_close=lambda close: print("Соединение закрыто"),
                                        timeout=10)
        
        if key == "start":
            print("Запускаем Websocket")
            self.my_client.kline(symbol=self.coin, interval=self.interval)
        if key == "stop":
            print("Останавливаем Websocket")
            self.my_client.stop()

    def message_handler_binance(self, _, message):
        if "result" in message:
            print(message)
        else: 
            # print(message) # ответ приходит строкой
            message = message[message.rfind("{"):].split('{')[1].rstrip('}').replace('"', '')
            dictionary = dict(subString.split(":") for subString in message.split(","))
            
            # print(f'dictionary {dictionary}')

            if dictionary["x"] == "true":
                print(dictionary)
                data = []
                data.append(self.setting_data, self.coin, self.interval, int(dictionary["t"]), float(dictionary["o"]), float(dictionary["h"]), float(dictionary["l"]), float(dictionary["c"]), float(dictionary["v"]))
                table_for_agent.insert_data(self.agent_name, data)
            
            self.queue.put(dictionary)
        

    def bybit(self, key):
        """
            Подключение к Websocket bybit 
            
            :key (str) - команда "start", "stop"
        """
        ws = WebSocket(
            testnet=True,
            channel_type="linear",
        )
        
        if key == "start":
            print("Запускаем Websocket")
            ws.kline_stream(interval=self.interval, symbol=self.coin, callback=self.message_handler_bybit)
        if key == "stop":
            print("Останавливаем Websocket")
            # ws.close()
    
    def message_handler_bybit(self, message):
            # print(message) # ответ приходит кортежем
            dictionary = message["data"][0]

            # print(f'dictionary {dictionary}')

            if message["data"][0]["confirm"] == True:

                print(dictionary)
                data = []
                data.append(self.setting_data, self.coin, self.interval, int(dictionary["start"]), float(dictionary["open"]), float(dictionary["high"]), float(dictionary["low"]), float(dictionary["close"]), float(dictionary["volume"]))
                table_for_agent.insert_data(self.agent_name, data)
            
            self.queue.put(dictionary)