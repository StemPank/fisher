import time
import setting as setting
from multiprocessing import Queue
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
import psycopg2
from psycopg2 import Error


def websocket_kline(queue=None):

    def message_handler(_, message):
        if "result" in message:
            print(message)
        else: 
            message = message[message.rfind("{"):].split('{')[1].rstrip('}').replace('"', '')
            dictionary = dict(subString.split(":") for subString in message.split(","))
            # print(dictionary)
            if queue != None:
                queue.put(dictionary)

            if dictionary['x'] == 'true':
                try:
                    connection = psycopg2.connect(user = setting.POSTGRES_USER,
                                    password=setting.POSTGRES_PASSWORD,
                                    host=setting.POSTGRES_HOST,
                                    port=setting.POSTGRES_PORT,
                                    database=setting.POSTGRES_DB)
                    cursor = connection.cursor()
                    cursor.execute('INSERT INTO binance_kline (name, market, time, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                            (dictionary['s'], 'folse', int(dictionary['t'])/1000, float(dictionary['o']), float(dictionary['h']), float(dictionary['l']), float(dictionary['c']), float(dictionary['v'])))
                    connection.commit()
                except (Exception, Error) as error:
                    print("Ошибка при работе с PostgreSQL %s", error)
                finally:
                    if connection:
                        cursor.close()
                        connection.close()

    print("Поднимаю Stream kline")
    client = SpotWebsocketStreamClient(on_message=message_handler, 
                                       on_close=lambda close: print("Соединение закрыто"), 
                                       timeout=10)
    
    for name in setting.NAME_SYMBOL:
            client.kline(symbol=name, interval="1m")

    try:
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        ...
    finally:
        client.stop()

    
    
if __name__ == "__main__":
    try:
        websocket_kline()
    except KeyboardInterrupt:
        ...


"""
    MARCKET
    1499040000000, // Время открытия Kline
    "0,01634790", // Цена открытия
    "0,80000000", // Высокая цена
    "0,01575800", // Низкая цена
    "0,01577100", // Цена закрытия
    "148976,11427815", // Объем
    1499644799999, // Время закрытия Kline
    "2434,19055334", // Объем котируемого актива
    308, // Количество сделок
    "1756,87402397", // Объем базового актива покупки тейкера
    "28,46694368", // Объем котируемого актива покупки тейкера
    "0" // Неиспользуемое поле, игнорировать.

    WEBSOCKET
    "k": {
        "t": 1672515780000, // Время начала Kline
        "T": 1672515839999, // Время закрытия Kline
        "s": "BNBBTC", // Символ
        "i": "1m", // Интервал
        "f": 100, // Идентификатор первой сделки
        "L": 200, // Идентификатор последней сделки
        "o": "0.0010", // Цена открытия
        "c": "0.0020", // Цена закрытия
        "h": "0.0025", // Высокая цена
        "l": "0.0015", // Низкая цена
        "v": "1000", // Объем базового актива
        "n": 100, // Количество сделок
        "x": false, // Закрыта ли эта kline?
        "q": "1.0000", // Объем котируемого актива
        "V": "500", // Объем базового актива тейкера, покупающего
        "Q": "0.500", // Объем котируемого актива тейкера, покупающего
        "B": "123456" // Игнорировать
    }
"""

