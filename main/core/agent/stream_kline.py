import os, sys, importlib
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
from pybit.unified_trading import WebSocketTrading, WebSocket

import core.agent.table_for_agent as table_for_agent

from utils.logging import logger_agent

class StreamKline():
    def __init__(self, agent_name, setting_data, setting_data_sub, key, coin=None, interval=None, queue=None):
        
        self.agent_name = agent_name
        self.setting_data = setting_data
        self.coin = coin
        self.interval = interval
        self.queue = queue
        self.setting_data_sub = setting_data_sub
        
        """
            hasattr(self, name): проверяет, есть ли у объекта метод с именем name.
            callable(getattr(self, name)): проверяет, является ли он вызываемым (т.е. функцией).
            getattr(self, name)(): если метод найден, он вызывается.
        """
        if hasattr(self, self.setting_data) and callable(getattr(self, self.setting_data)):
            # Вызываем метор с именем ↓,   передаем аргументы ↓
            getattr(self, self.setting_data)(key) 
        else:
            logger_agent.info(f"Метод '{self, self.setting_data}' не найден.")

    

    def binance(self, key):
        """
            Подключение к Websocket binance 

            :key (str) - команда "start", "stop"
        """

        if self.setting_data_sub == "test":
            self.setting_data_sub = "wss://ws-api.testnet.binance.vision/ws-api/v3"
        if self.setting_data_sub != "test":
            self.setting_data_sub = "wss://stream.binance.com:9443"

        self.my_client = SpotWebsocketStreamClient(stream_url=self.setting_data_sub,
                                                   on_message=self.message_handler_binance, 
                                                    on_close=lambda close: print("Соединение закрыто"),
                                                    timeout=10)
        
        if key == "start":
            logger_agent.info("Запускаем Websocket")
            self.my_client.kline(symbol=self.coin, interval=self.interval)
        if key == "stop":
            logger_agent.info("Останавливаем Websocket")
            self.my_client.stop()

    def message_handler_binance(self, _, message):
        if "result" in message:
            logger_agent.info(message)
        else: 
            # print(message) # ответ приходит строкой
            message = message[message.rfind("{"):].split('{')[1].rstrip('}').replace('"', '')
            dictionary = dict(subString.split(":") for subString in message.split(","))
            
            # print(f'dictionary {dictionary}')

            if dictionary["x"] == "true":
                logger_agent.debug("Сигнал WebSocket о закрытии свечи")
                data = []
                data.append((self.setting_data, self.coin, self.interval, int(dictionary["t"]), float(dictionary["o"]), float(dictionary["h"]), float(dictionary["l"]), float(dictionary["c"]), float(dictionary["v"])))
                logger_agent.debug(f"Cписок для записи в БД {data}")
                table_for_agent.insert_data_stream(self.agent_name, data)
            
            self.queue.put(dictionary)
        

    def bybit(self, key):
        """
            Подключение к Websocket bybit 
            
            :key (str) - команда "start", "stop"
        """

        if self.setting_data_sub == "test":
            self.setting_data_sub = True
        if self.setting_data_sub != "test":
            self.setting_data_sub = False

        ws = WebSocket(
            testnet=self.setting_data_sub,
            channel_type="linear",
        )
        
        if key == "start":
            logger_agent.info("Запускаем Websocket")
            ws.kline_stream(interval=self.interval, symbol=self.coin, callback=self.message_handler_bybit)
        if key == "stop":
            logger_agent.info("Останавливаем Websocket")
            # ws.close()
    
    def message_handler_bybit(self, message):
            # print(message) # ответ приходит кортежем
            dictionary = message["data"][0]

            # print(f'dictionary {dictionary}')

            if dictionary["confirm"] == True:
                logger_agent.debug("Сигнал WebSocket о закрытии свечи")
                data = []
                try:
                    data.append((self.setting_data, self.coin, self.interval, int(dictionary["start"]), float(dictionary["open"]), float(dictionary["high"]), float(dictionary["low"]), float(dictionary["close"]), float(dictionary["volume"])))
                except Exception as e:
                    logger_agent.warning(f"Ошибка формирования списка WebSocket {e}")
                logger_agent.debug(f"Cписок для записи в БД {data}")
                table_for_agent.insert_data_stream(self.agent_name, data)
            
            self.queue.put(dictionary)