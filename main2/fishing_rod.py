import tkinter as tk
from tkinter import ttk, Scrollbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Slider
from mplfinance.original_flavor import candlestick_ohlc
from multiprocessing import Queue
import datetime, time, threading
import numpy as np


class GraphApp:
    def __init__(self, root, queue_kline_gui: Queue, queue_depth_gui: Queue, queue_kline: Queue, queue_depth: Queue, shared_data):
        self.debugging = True
        
        self.root = root
        self.queue_kline_gui = queue_kline_gui
        self.queue_depth_gui = queue_depth_gui
        self.queue_kline = queue_kline
        self.queue_depth = queue_depth
        self.shared_data = shared_data

        self.running = False
        self.data = []  # Исторические данные для графика
        self.lines = []  # Хранилище пользовательских линий
        self.current_line = None  # Временная линия для создания
        self.selected_line = None  # Выделенная линия для редактирования
        self.selected_end = None  # Конец линии, который редактируется ("start" или "end")

        self.coin = "BTCUSDT"  # Монета по умолчанию
        self.shared_data["command"] = {"type": "change_coin", "coin": self.coin}
        self.order_book_data = {"b": [], "a": []}  # Данные стакана

        # График
        self.figure, self.ax = plt.subplots(figsize=(8, 5))
        self.ax.set_title(f"График {self.coin}")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Цена")
        self.canvas = FigureCanvasTkAgg(self.figure, root)
        self.canvas.get_tk_widget().grid(column=0, row=1, columnspan=2, rowspan=2, padx=0, pady=0)
        
        # Виджет для отображения стакана
        self.order_book_frame = tk.Frame(root)
        self.order_book_frame.grid(column=3, row=1, columnspan=2, rowspan=2, padx=0, pady=0)

        self.order_book_listbox = tk.Listbox(self.order_book_frame, height=25, width=30)
        self.order_book_listbox.pack()

        # Центрируем стакан
        # self.last_price_label = tk.Label(self.order_book_frame, text="---", font=("Arial", 12, "bold"), fg="blue")
        # self.last_price_label.pack()

        # Выпадающий список для выбора монеты
        self.coin_var = tk.StringVar(value=self.coin)
        self.coin_selector = ttk.Combobox(root, textvariable=self.coin_var, values=["BTCUSDT", "ETHUSDT", "BNBUSDT"], state="readonly")
        self.coin_selector.grid(row=0, column=0, padx=5, pady=5)
        self.coin_selector.bind("<<ComboboxSelected>>", self.change_coin)

        # Элементы интерфейса
        self.start_button = ttk.Button(root, text="Старт", command=self.start_processing)
        self.start_button.grid(row=0, column=2, padx=5, pady=5)

        self.stop_button = ttk.Button(root, text="Стоп", command=self.stop_processing)
        self.stop_button.grid(row=0, column=3, padx=5, pady=5)

        self.add_indicator_button = ttk.Button(root, text="Добавить индикатор", command=self.add_indicator)
        self.add_indicator_button.grid(row=0, column=1, padx=5, pady=5)

        # Подключаем события мыши
        self.canvas.mpl_connect("button_press_event", self.on_mouse_click)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

        self.update_chart()
        self.update_order_book()
        self.add_scrollbar()

    def change_coin(self, event):
        """Изменяем монету, очищаем график и начинаем загружать новые данные"""
        self.coin = self.coin_var.get()
        self.data.clear()  # Очищаем данные
        self.lines.clear()  # Очищаем данные
        self.ax.clear()  # Очищаем график
        self.ax.set_title(f"График {self.coin}")
        self.ax.set_xlabel("Время")
        self.ax.set_ylabel("Цена")
        self.order_book_data = {"b": [], "a": []}  # Сбрасываем стакан
        self.shared_data["command"] = {"type": "change_coin", "coin": self.coin}
        self.update_chart()

    def update_chart(self):
        """Обновляем график на основе данных из очереди."""
        new_data_added = False
        while not self.queue_kline_gui.empty():
            new_data = self.queue_kline_gui.get()
            if new_data["s"] == self.coin:
                # Преобразуем временную метку в дату
                timestamp_ms = new_data["t"]
                timestamp = datetime.datetime.fromtimestamp(int(timestamp_ms) / 1000)
                if self.data and mdates.date2num(timestamp) == self.data[-1][0]:
                    # Обновляем последнюю свечу
                    self.data[-1][2] = max(self.data[-1][2], round(float(new_data["h"]), 2))  # High
                    self.data[-1][3] = min(self.data[-1][3], round(float(new_data["l"]), 2))  # Low
                    self.data[-1][4] = round(float(new_data["c"]), 2)  # Close
                else:
                    # Добавляем новую свечу
                    self.data.append([
                        mdates.date2num(timestamp),
                        round(float(new_data["o"]), 2),
                        round(float(new_data["h"]), 2),
                        round(float(new_data["l"]), 2),
                        round(float(new_data["c"]), 2)
                    ])
                    new_data_added = True

        if self.data:
            if new_data_added:
                self.ax.clear()
                self.ax.set_title(f"График {self.coin}")
                self.ax.set_xlabel("Время")
                self.ax.set_ylabel("Цена")
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
                self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))

                # Рисуем свечи
                candlestick_ohlc(self.ax, self.data, width=0.0005, colorup='green', colordown='red', alpha=0.8)

                # Рисуем линии
                for line in self.lines:
                    self.ax.plot(line["x"], line["y"], color="blue", linewidth=1.5)

                # Рисуем текущую линию, если она создаётся
                if self.current_line:
                    self.ax.plot(self.current_line["x"], self.current_line["y"], color="orange", linestyle="--")

                # Устанавливаем видимую область (последние 50 свечей)
                if len(self.data) > 50:
                    self.ax.set_xlim(self.data[-50][0], self.data[-1][0])

                # Перерисовываем график
                self.canvas.draw()

        # Обновляем график через 1 секунду
        self.root.after(1000, self.update_chart)

    def update_order_book(self):
        """Обновляем стакан на основе данных из очереди"""
        while not self.queue_depth_gui.empty():
            new_data = self.queue_depth_gui.get()
            self.order_book_data = new_data

        if self.order_book_data:
            self.order_book_listbox.delete(0, tk.END) # Очистка содержимого стакана

            # Центровка на последней цене
            last_price = self.data[-1][4] if self.data else 0 # Достаем последнюю цену закрытия если в списке data чтото есть, если нет то 0
            # self.last_price_label.config(text=f"Последняя цена: {last_price}")

            # Добавляем asks (покупки)
            self.order_book_listbox.insert(tk.END, "ASKS:")
            for price, qty in reversed(self.order_book_data["a"][:10]):
                self.order_book_listbox.insert(tk.END, f"{float(price):.2f} | {float(qty):.2f}")

            # Добавляем разделитель
            self.order_book_listbox.insert(tk.END, "-" * 20)

            # Добавляем bids (продажи)
            self.order_book_listbox.insert(tk.END, "BIDS:")
            for price, qty in self.order_book_data["b"][:10]:
                self.order_book_listbox.insert(tk.END, f"{float(price):.2f} | {float(qty):.2f}")

        # Обновление стакана через 500 мс
        self.root.after(500, self.update_order_book)

    def add_scrollbar(self):
        """Добавляем горизонтальную полосу прокрутки для управления графиком"""
        # Создаём полосу прокрутки
        self.scrollbar = Scrollbar(self.root, orient="horizontal")
        self.scrollbar.grid(column=0, row=3, columnspan=2, sticky="we")

        # Устанавливаем максимальное значение полосы прокрутки
        # scrollbar.config(command=self.on_scrollbar)
        # self.scrollbar = scrollbar  # Сохраняем ссылку для управления

        # Устанавливаем команду прокрутки
        self.scrollbar.config(command=self.on_scrollbar)
        self.scrollbar.set(1.0, 1.0) 

    def on_scrollbar(self, *args):
        """Обновляем видимую область графика при изменении полосы прокрутки"""
        if not self.data:
            return

        # Общий диапазон индексов свечей
        total_candles = len(self.data)
        visible_candles = 50  # Количество свечей, видимых одновременно

        # Значение от полосы прокрутки
        if args[0] == "moveto":
            scroll_position = float(args[1])  # Преобразуем значение прокрутки в число
        else:
            return

        # Рассчитываем начальный индекс видимой области
        max_start_index = max(0, total_candles - visible_candles)
        start_index = int(scroll_position * max_start_index)
        end_index = start_index + visible_candles

        # Ограничиваем индексы в пределах данных
        start_index = max(0, start_index)
        end_index = min(total_candles, end_index)

        # Устанавливаем видимую область графика
        self.ax.set_xlim(self.data[start_index][0], self.data[end_index - 1][0])
        self.canvas.draw()

        # Обновляем положение полосы прокрутки
        if total_candles > visible_candles:
            self.scrollbar.set(start_index / total_candles, end_index / total_candles) 


    def on_mouse_click(self, event):
        """Обработка кликов мыши."""
        if event.button == 1:  # ЛКМ
            if not event.inaxes:
                # Клик вне графика отменяет текущую линию
                if self.debugging:
                    print('Клик вне графика')
                self.current_line = None
                self.selected_line = None
                self.selected_end = None
            else:
                # Проверяем, попали ли на линию
                for line in self.lines:
                    if self.is_point_near_line(event.xdata, event.ydata, line):
                        self.selected_line = line
                        self.selected_end = self.get_closest_end(event.xdata, event.ydata, line)
                        if self.debugging:
                            print('Клик вне графика')
                        return

                # Если линия не выбрана, начинаем рисовать новую
                if self.current_line is None:
                    if self.debugging:
                        print('Начало новой линии')
                    self.current_line = {
                        "x": [event.xdata, event.xdata],
                        "y": [event.ydata, event.ydata],
                    }
                else:
                    # Завершаем рисование новой линии
                    if self.debugging:
                        print('Конец новой линии')
                    self.current_line["x"][1] = event.xdata
                    self.current_line["y"][1] = event.ydata
                    self.lines.append(self.current_line)
                    self.current_line = None
                    self.update_chart()
                    self.canvas.draw()
        elif event.button == 3:  # ПКМ
            if self.debugging:
                print('Клик ПКМ')
            self.delete_line_at(event.xdata, event.ydata)

    def is_point_near_line(self, x, y, line, tolerance=0.01):
        """Проверяет, находится ли точка (x, y) рядом с линией."""
        x1, x2 = line["x"]
        y1, y2 = line["y"]
        # Уравнение прямой: Ax + By + C = 0
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2

        # Проверка деления на ноль
        if A==0 and B==0:
            return False

        # Расстояние от точки до прямой
        try:
            distance = abs(A * x + B * y + C) / ((A**2 + B**2) ** 0.5)
        except ZeroDivisionError:
            return False

        # Проверяем, находится ли точка в пределах линии
        in_bounds = min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)
        return distance <= tolerance and in_bounds
    
    def get_closest_end(self, x, y, line):
        """Возвращает ближайший конец линии ('start' или 'end')."""
        start_dist = ((x - line["x"][0])*2 + (y - line["y"][0])*2) ** 0.5
        end_dist = ((x - line["x"][1])*2 + (y - line["y"][1])*2) ** 0.5
        return "start" if start_dist < end_dist else "end"
    
    def delete_line_at(self, x, y):
        """Удаляет линию, если клик ПКМ попадает на неё."""
        tolerance = 0.03  # Допустимое отклонение для попадания на линию
        for line in self.lines:
            x1, x2 = line["x"]
            y1, y2 = line["y"]

            # Проверка попадания на линию
            if self.is_point_near_line1(x, y, x1, y1, x2, y2, tolerance):
                self.lines.remove(line)
                self.update_chart()
                break
    @staticmethod
    def is_point_near_line1(x, y, x1, y1, x2, y2, tolerance):
        """Проверяет, находится ли точка (x, y) рядом с линией."""
        # Уравнение прямой: Ax + By + C = 0
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2

        # Проверка деления на ноль
        if A==0 and B==0:
            return False
        
        # Расстояние от точки до прямой
        try:
            distance = abs(A * x + B * y + C) / ((A**2 + B**2) ** 0.5)
        except ZeroDivisionError:
            return False

        # Проверка, попадает ли точка в интервал линии
        in_bounds = min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)
        return distance <= tolerance and in_bounds

    def on_mouse_release(self, event):
        """Обработка отпускания мыши."""
        if event.button == 1:  # ЛКМ
            # Завершаем перемещение линии
            if self.debugging:
                print('Отпускания мыши')
            self.selected_line = None
            self.selected_end = None
    
    def on_mouse_move(self, event):
        """Обработка движения мыши."""
        if self.current_line and event.inaxes:
            # Обновляем текущую линию при создании
            self.current_line["x"][1] = event.xdata
            self.current_line["y"][1] = event.ydata
            self.update_chart()
            self.canvas.draw()
        elif self.selected_line and self.selected_end and event.inaxes:
            # Перемещаем выбранный конец линии
            if self.selected_end == "start":
                self.selected_line["x"][0] = event.xdata
                self.selected_line["y"][0] = event.ydata
            elif self.selected_end == "end":
                self.selected_line["x"][1] = event.xdata
                self.selected_line["y"][1] = event.ydata
            self.update_chart()
            self.canvas.draw()


    def start_processing(self):
        """Запуск обработки данных."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.process_data, daemon=True)
            self.thread.start()

    def stop_processing(self):
        """Остановка обработки данных."""
        self.running = False

    def process_data(self):
        while self.running:
            print('Работает')

            time.sleep(1)

    def add_indicator(self):
        """Добавляет пользовательский индикатор на график."""
        if not self.data:
            return

        # Пример: добавление простой скользящей средней
        closes = np.array([d[4] for d in self.data])  # Цена закрытия
        sma = np.convolve(closes, np.ones(10)/10, mode='valid')

        x_data = [d[0] for d in self.data[-len(sma):]]
        self.ax.plot(x_data, sma, label="SMA(10)", color="orange")
        self.ax.legend()
        self.canvas.draw()


"""
grid(   column=номер столбца, 
        row=номер строки, 
        columnspan=сколько столбцов должен занимать элемент,
        rowspan=сколько строк должен занимать элемент,
        ipadx и ipady отступы по горизонтали и вертикали от границ элемента
        padx и pady отступы по горизонтали и вертикали от границ ячейки грида до границ элемента
        sticky=выравнивание элемента в ячейке если ячейка больше элемента
    )
"""