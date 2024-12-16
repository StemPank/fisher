import time
from multiprocessing import Queue
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient

class BinanceWebKline:
    def __init__(self, queue_kline: Queue, queue_kline_gui: Queue):
        self.ws_client = SpotWebsocketStreamClient(on_message=self.message_handler, 
                                        on_close=lambda close: print("Соединение закрыто"),
                                        timeout=10)
        self.current_pair = None

        self.queue_kline = queue_kline
        self.queue_kline_gui = queue_kline_gui

    def start_socket(self, pair):
        """Запускает веб-сокет для указанной валюты"""
        if self.current_pair == pair:
            return # если пара не изменилась, ничего не делать
        
        # Закрываем текущее соединение, если уже установлено
        if self.current_pair:
            print(f'Закрытие соединения для {self.current_pair}')
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
        print(f'Подключение {pair}')
        try:
            self.ws_client.kline(symbol=pair, interval="1m")
        except Exception as e:
            print(f'Ошибка подключения к depth для {pair}: {e}')


    def message_handler(self, _, message):
        if "result" in message:
            print(message)
        else: 
            message = message[message.rfind("{"):].split('{')[1].rstrip('}').replace('"', '')
            dictionary = dict(subString.split(":") for subString in message.split(","))
            
            # print(f'dictionary {dictionary}')
            # print(f'отладка очереди {self.queue_kline}')
            self.queue_kline.put(dictionary)
            self.queue_kline_gui.put(dictionary)

    def stop_socket(self):
        """Останавливает текущее соединение"""
        if self.current_pair:
            print(f'Закрытие соединения для {self.current_pair}')
            self.ws_client.stop()
            self.current_pair = None

def websocket_kline(queue_kline: Queue, queue_kline_gui: Queue, shared_data):
    """Функция для запуска веб-сокета"""
    ws = BinanceWebKline(queue_kline, queue_kline_gui)
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
    from multiprocessing import Process, Queue, Manager
    with Manager() as manager:
        queue_kline_gui = Queue()
        queue_kline = Queue()
        shared_data = manager.dict()
        shared_data["command"] = {"type": "change_coin", "coin": "BTCUSDT"}

        try:
            websocket_kline(queue_kline, queue_kline_gui, shared_data)
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

