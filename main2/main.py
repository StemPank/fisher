import tkinter as tk
import multiprocessing
from multiprocessing import Process, Queue, Manager
from stream_kline_binance import websocket_kline
from historical_data import historical_data 
from stream_depth_binance import websocket_depth
from fishing_rod import GraphApp

def start_websocket_kline(queue_kline: Queue, queue_kline_gui: Queue, shared_data):
    websocket_kline(queue_kline, queue_kline_gui, shared_data)

def start_websocket_depth(queue_depth: Queue, queue_depth_gui: Queue, shared_data):
    websocket_depth(queue_depth, queue_depth_gui, shared_data)

def start_historical_data(queue_kline: Queue, queue_kline_gui: Queue, shared_data):
    historical_data(queue_kline, queue_kline_gui, shared_data)

def start_gui(queue_kline_gui: Queue, queue_depth_gui: Queue, queue_kline: Queue, queue_depth: Queue, 
              stop_event, processes, shared_data):
    """Запускаем GUI и добавляем обработчик закрытия."""
    def finish():
        """Обработчик закрытия окна GUI."""
        # Ставим сигнал для завершения
        stop_event.set()
        # Завершаем процессы
        for process in processes:
            process.terminate()
            process.join()
        root.destroy() # ручное закрытие окна и всего приложения
        print('Закрытие приложения')
    root = tk.Tk()
    app = GraphApp(root, queue_kline_gui, queue_depth_gui, queue_kline, queue_depth, shared_data)
    # Связываем закрытие окна с завершением процессов
    root.protocol("WM_DELETE_WINDOW", finish)
    root.mainloop()


if __name__ == "__main__":
 
    with Manager() as manager:
        queue_kline_gui = Queue()
        queue_kline = Queue()
        queue_depth_gui = Queue()
        queue_depth = Queue()
        shared_data = manager.dict()
        shared_data["command"] = None

        stop_event = multiprocessing.Event()

        WebKline = Process(target=start_websocket_kline, args=(queue_kline, queue_kline_gui, shared_data))
        WebKline.start()
        WebDepth = Process(target=start_websocket_depth, args=(queue_depth, queue_depth_gui, shared_data))
        WebDepth.start()
        HisKline = Process(target=start_historical_data, args=(queue_kline, queue_kline_gui, shared_data))
        HisKline.start()
        processes=[WebKline, WebDepth, HisKline]

        try:
            start_gui(queue_kline_gui, queue_depth_gui, queue_kline, queue_depth, stop_event, processes, shared_data)
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join()