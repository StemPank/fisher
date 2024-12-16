from multiprocessing import Queue
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
import time, ast

class BinanceWebDepth:
    def __init__(self, queue_depth: Queue, queue_depth_gui: Queue):
        self.ws_client = SpotWebsocketStreamClient(on_message=self.message_handler, 
                                        on_close=lambda close: print("Закрыто depth-cоединение"),
                                        timeout=20)
        self.current_pair = None

        self.queue_depth = queue_depth
        self.queue_depth_gui = queue_depth_gui

    def start_socket(self, pair):
        """Запускает веб-сокет для указанной валюты"""
        if self.current_pair == pair:
            return # если пара не изменилась, ничего не делать
        
        # Закрываем текущее соединение, если уже установлено
        if self.current_pair:
            print(f'Закрытие depth-соединения для {self.current_pair}')
            self.ws_client.stop()
            try:
                self.ws_client = SpotWebsocketStreamClient(on_message=self.message_handler, 
                                        on_close=lambda close: print("Соединение закрыто"),
                                        timeout=20)
            except Exception as e:
                print(f'Ошибка пересоздания клиента depth для {e}')

        # Устанавливаем новую валютную пару
        self.current_pair = pair

        # Запуск нового подключения
        print(f'Подключение depth для {pair}...')
        try:
            self.ws_client.diff_book_depth(symbol=pair, interval="1m")
        except Exception as e:
            print(f'Ошибка подключения к depth для {pair}: {e}')

    def message_handler(self, _, message):
        if "result" in message:
            print(message)
        else: 
            # print(message)
            data = message.split(',"b"', 1)[0].split('{')[1].replace('"', '')
            data = dict(subString.split(":") for subString in data.split(","))
            higher = message[message.rfind("[["):].rstrip('}')
            higher = ast.literal_eval(higher)
            below = message[message.find("[["):].split(']]', 1)[0]+']]'
            below = ast.literal_eval(below)
            data["b"]= below
            data["a"]= higher
            self.queue_depth.put(data)
            self.queue_depth_gui.put(data)

    def stop_socket(self):
        """Останавливает текущее соединение"""
        if self.current_pair:
            print(f'Закрытие соединения для {self.current_pair}')
            self.ws_client.stop()
            self.current_pair = None

def websocket_depth(queue_depth: Queue, queue_depth_gui: Queue, shared_data):
    """Функция для запуска веб-сокета"""
    ws = BinanceWebDepth(queue_depth, queue_depth_gui)
    try:
        while True:
            # Проверяем, изменилась ли валюта
            current_pair = shared_data.get("command")
            current_pair = current_pair["coin"]
            if current_pair:
                ws.start_socket(current_pair)
            time.sleep(1)
    except KeyboardInterrupt:
        ws.stop_socket()
    
    
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

