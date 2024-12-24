from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QListWidget, QLabel
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from pyqtgraph import PlotWidget, mkPen
import pyqtgraph as pg
import numpy as np
import datetime
from multiprocessing import Queue
import threading
import time

class GraphApp(QMainWindow):
    def __init__(self, queue_kline_gui: Queue = Queue(), queue_depth_gui: Queue = Queue(), queue_kline: Queue = Queue(), queue_depth: Queue = Queue(), shared_data=None):
        super().__init__()

        self.debag = True
        # Инициализация данных
        self.setWindowTitle("Торговый график с PyQt5 и PyQtGraph")
        self.resize(1200, 800)
        self.queue_kline_gui = queue_kline_gui
        self.queue_depth_gui = queue_depth_gui
        self.queue_kline = queue_kline
        self.queue_depth = queue_depth
        self.shared_data = shared_data if shared_data else {}

        self.running = False
        self.data = []  # Исторические данные для графика
        self.lines = []  # Хранилище пользовательских линий
        self.current_line = None  # Временная линия для создания
        self.selected_line = None  # Выделенная линия для редактирования
        self.selected_end = None  # Конец линии, который редактируется ("start" или "end")
        self.coin = "BTCUSDT"  # Текущая монета
        self.shared_data["command"] = {"type": "change_coin", "coin": self.coin}
        self.order_book_data = {"b": [], "a": []}  # Данные стакана

        self.init_ui()

    def init_ui(self):
        """Создаём элементы интерфейса."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Основной макет
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Верхний блок (выбор монеты, кнопки управления)
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout)

        # Выбор монеты
        self.coin_selector = QComboBox()
        self.coin_selector.addItems(["BTCUSDT", "ETHUSDT", "BNBUSDT"])
        self.coin_selector.currentIndexChanged.connect(self.change_coin)
        control_layout.addWidget(self.coin_selector)

        # Кнопка "Старт"
        self.start_button = QPushButton("Старт")
        self.start_button.clicked.connect(self.start_processing)
        control_layout.addWidget(self.start_button)

        # Кнопка "Стоп"
        self.stop_button = QPushButton("Стоп")
        self.stop_button.clicked.connect(self.stop_processing)
        control_layout.addWidget(self.stop_button)

        # Кнопка "Добавить индикатор"
        self.add_indicator_button = QPushButton("Добавить индикатор")
        self.add_indicator_button.clicked.connect(self.add_indicator)
        control_layout.addWidget(self.add_indicator_button)

        # График и стакан
        graph_and_order_layout = QHBoxLayout()
        main_layout.addLayout(graph_and_order_layout)

        # График
        self.graph_widget = PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setLabel("left", "Цена")
        self.graph_widget.setLabel("bottom", "Время")
        graph_and_order_layout.addWidget(self.graph_widget)

        # Стакан (список)
        self.order_book_list = QListWidget()
        self.order_book_list.setFixedWidth(200)  # Задаем ширину стакана
        graph_and_order_layout.addWidget(self.order_book_list)

        self.update_chart()
        self.update_order_book()
        
        # Обновление графика каждую секунду
        self.chart_update_timer = QTimer()
        self.chart_update_timer.timeout.connect(self.update_chart)
        self.chart_update_timer.start(1000)  # Обновление каждую секунду
        
        self.order_book_update_timer = QTimer()
        self.order_book_update_timer.timeout.connect(self.update_order_book)
        self.order_book_update_timer.start(1000)  # Обновление каждую секунду

    def change_coin(self):
        """Обновляем монету и очищаем график."""
        self.coin = self.coin_selector.currentText()
        self.data.clear()
        self.lines.clear()
        self.graph_widget.clear()
        self.order_book_data = {"b": [], "a": []}  # Сбрасываем стакан
        self.shared_data["command"] = {"type": "change_coin", "coin": self.coin}

    def update_chart(self):
        """Обновляем график."""
        new_data_added = False

        # Получение новых данных
        while not self.queue_kline_gui.empty():
            new_data = self.queue_kline_gui.get()
            # if self.debag:
            #     print(f'Дебагинг, очередь queue_kline_gui {new_data}')
            if new_data["s"] == self.coin:
                timestamp = datetime.datetime.fromtimestamp(int(new_data["t"]) / 1000).timestamp()
                ohlc = [timestamp, 
                        round(float(new_data["o"]), 2), 
                        round(float(new_data["h"]), 2), 
                        round(float(new_data["l"]), 2), 
                        round(float(new_data["c"]), 2)]

                if self.data and timestamp == self.data[-1][0]:
                    # Обновляем последнюю свечу
                    self.data[-1] = ohlc
                else:
                    # Добавляем новую свечу
                    self.data.append(ohlc)
                    new_data_added = True

        # Обновление графика
        if new_data_added:
            # self.graph_widget.clear()
            x = [d[0] for d in self.data]
            o = [float(d[1]) for d in self.data]  # Open
            h = [float(d[2]) for d in self.data]  # High
            l = [float(d[3]) for d in self.data]  # Low
            c = [float(d[4]) for d in self.data]  # Close
            
            # Задаем ширину свечей в зависимости от диапазона времени
            width = (max(x) - min(x)) / len(x) * 0.8  

            # Рисуем свечи
            for i in range(len(self.data)):
                # Определяем цвет свечи
                color = "g" if c[i] >= o[i] else "r"  # Зеленая для роста, красная для падения

                # Рисуем тень свечи
                self.graph_widget.plot([x[i], x[i]], [l[i], h[i]], pen=mkPen(color, width=1))

                # Рисуем тело свечи (прямоугольник)
                rect = pg.BarGraphItem(x=[x[i]], height=[abs(c[i] - o[i])],
                                    width=width, y=min(o[i], c[i]), brush=color)
                self.graph_widget.addItem(rect)

    def update_order_book(self):
        """Обновляем стакан."""
        while not self.queue_depth_gui.empty():
            new_data = self.queue_depth_gui.get()
            self.order_book_data = new_data

        if self.order_book_data:
            self.order_book_list.clear()
            self.order_book_list.addItem("ASKS:")
            for price, qty in reversed(self.order_book_data["a"][:20]):
                self.order_book_list.addItem(f"{float(price):.2f} | {float(qty):.2f}")
            self.order_book_list.addItem("-" * 20)
            self.order_book_list.addItem("BIDS:")
            for price, qty in self.order_book_data["b"][:20]:
                self.order_book_list.addItem(f"{float(price):.2f} | {float(qty):.2f}")

        # Обновление через 500 мс
        # threading.Timer(0.5, self.update_order_book).start()

    def add_indicator(self):
        """Добавление индикатора (скользящее среднее)."""
        if not self.data:
            return
        closes = np.array([d[4] for d in self.data[-50:]])
        sma = np.convolve(closes, np.ones(10) / 10, mode='valid')
        x_data = [d[0] for d in self.data[-len(sma):]]
        line = pg.PlotDataItem(x_data, sma, pen=pg.mkPen("orange", width=2))
        self.plot_widget.addItem(line)

    def start_processing(self):
        if not self.running:
            self.running = True
            self.worker = WorkerThread(self.queue_kline, self.queue_depth)
            self.worker.start()

    def stop_processing(self):
        if self.running:
            self.running = False
            self.worker.stop()


class WorkerThread(QThread):
    new_data_signal = pyqtSignal(dict)
    new_order_book_signal = pyqtSignal(dict)

    def __init__(self, queue_kline: Queue, queue_depth: Queue):
        super().__init__()
        self.queue_kline = queue_kline
        self.queue_depth = queue_depth
        self.running = True

    def run(self):
        while self.running:
            print('Работает')

            time.sleep(1)  # simulate waiting for new data

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


if __name__ == "__main__":
    from multiprocessing import Queue, Manager
    from PyQt5.QtWidgets import QApplication
    import sys
    with Manager() as manager:
        queue_kline_gui = Queue()
        queue_kline = Queue()
        queue_depth_gui = Queue()
        queue_depth = Queue()
        shared_data = manager.dict()
        shared_data["command"] = None

        app = QApplication(sys.argv)
        main_window = GraphApp(queue_kline_gui, queue_depth_gui, queue_kline, queue_depth, shared_data)  # Инициализируем графическое приложение
        main_window.show()  # Показываем главное окно
        sys.exit(app.exec_())  # Запускаем главный цикл приложени
