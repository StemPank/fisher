import time
import setting as setting
import ast
from multiprocessing import Queue
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
import psycopg2
from psycopg2 import Error


def websocket_depth(queue_depth=None):

    def message_handler(_, message):
        if "result" in message:
            print(message)
        else: 
            # print(message)
            data = message.split(',"b"', 1)[0].split('{')[1].replace('"', '')
            data = dict(subString.split(":") for subString in data.split(","))
            # print(f'data: {data}')
            higher = message[message.rfind("[["):].rstrip('}')
            higher = ast.literal_eval(higher)
            # print(f'higher: {len(higher)}')
            below = message[message.find("[["):].split(']]', 1)[0]+']]'
            below = ast.literal_eval(below)
            # print(f'below: {below}')
            data["b"]= below
            data["a"]= higher
            # print(f'all: {data}')
            if queue_depth != None:
                queue_depth.put(data)


    print("Поднимаю Stream depth")
    client = SpotWebsocketStreamClient(on_message=message_handler, 
                                       on_close=lambda close: print("Соединение закрыто"), 
                                       timeout=10)
    
    for name in setting.NAME_SYMBOL:
            client.diff_book_depth(symbol=name, speed=1000)

    try:
        while True: 
            time.sleep(1)
    except KeyboardInterrupt:
        ...
    finally:
        client.stop()

    
    
if __name__ == "__main__":
    try:
        websocket_depth()
    except KeyboardInterrupt:
        ...


"""
    Diff. Depth Stream
    Дифференциальный поток глубины
    Обновления цен и глубины количества в книге заказов используются для локального управления книгой заказов.
    {
        "e": "depthUpdate",     // Тип события
        "E": 1672515782136,     // Время события
        "s": "BNBBTC",          // Символ
        "U": 157,               // Первый идентификатор обновления в событии
        "u": 160,               // Последний идентификатор обновления в событии
        "b": [                  // На покупку
                [
                "0.0024",       // Уровень цен для обновления
                "10"            // Количество
                ]
            ],
        "a": [                  // На продажу
                [
                "0.0026",       // Уровень цен для обновления
                "100"           // Количество
                ]
            ]
    }

    Partial Book Depth Streams
    Top bids and asks, Valid are 5, 10, or 20.
    Частичные потоки глубины книги
    Лучшие биды и аски, действительны 5, 10 или 20.
    {
        "lastUpdateId": 160,    // Последний идентификатор обновления
        "bids": [               // На покупку
                    [
                    "0.0024",   // Уровень цен для обновления
                    "10"        // Количество
                    ]
                ],
        "asks": [               // На продажу
                    [
                    "0.0026",   // Уровень цен для обновления
                    "100"       // Количество
                    ]
                ]
    }
"""

