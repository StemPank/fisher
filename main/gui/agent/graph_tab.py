import time, random
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox, QCheckBox, QHBoxLayout, QGridLayout, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
import core.gui.table_for_agent as table_for_agent
from utils.logging import logger


class GraphUpdater(QThread):
    """Поток обновления графика раз в минуту"""
    data_updated = pyqtSignal(list)  # Сигнал для передачи данных в основной поток

    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        self.running = True  # Флаг работы потока

    def run(self):
        """Запускает цикл обновления раз в 60 секунд"""
        while self.running:
            data = self.fetch_candle_data()
            self.data_updated.emit(data)  # Отправляем данные в основной поток
            time.sleep(60)  # Обновление раз в минуту

    def fetch_candle_data(self):
        """Загружает данные свечей из SQLite"""
        try:
            return table_for_agent.get_data_main_table(self.agent_name)
        except Exception as e:
            logger.warning(f"Ошибка загрузки данных: {e}")
            return []


class GraphTab(QWidget):
    """Вкладка с графиком и индикаторами"""

    def __init__(self, agent_name, language):
        super().__init__()
        self.agent_name = agent_name
        self.language = language
        self.layout = QVBoxLayout(self)

        # Выбор типа графика
        self.graph_type_selector = QComboBox()
        self.graph_type_selector.addItems(["Линия", "Свечи"])
        self.graph_type_selector.currentIndexChanged.connect(self.update_graph)
        self.layout.addWidget(self.graph_type_selector)

        # Кнопка обновления
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.manual_update)
        self.layout.addWidget(refresh_button)

        # Виджет графика
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setLabel("left", "Цена")
        self.graph_widget.setLabel("bottom", "Время")
        self.layout.addWidget(self.graph_widget)

        # **Контейнер для списка индикаторов**
        self.indicator_layout = QGridLayout()
        self.layout.addLayout(self.indicator_layout)
        self.indicator_checkboxes = {}
        self.indicator_plots = {}  # Храним нарисованные индикаторы

        # Запуск потока обновления
        self.graph_thread = GraphUpdater(self.agent_name)
        self.graph_thread.data_updated.connect(self.update_graph)

        # self.load_indicators()

    def load_indicators(self):
        """Загружает список индикаторов и добавляет чекбоксы"""
        # Сохраняем текущее состояние чекбоксов
        previous_states = {name: checkbox.isChecked() for name, (checkbox, _) in self.indicator_checkboxes.items()}

        # Очищаем старые индикаторы
        for i in reversed(range(self.indicator_layout.count())):
            self.indicator_layout.itemAt(i).widget().setParent(None)  # Очищаем старые индикаторы

        self.indicator_checkboxes = {}
        indicator_list = table_for_agent.get_list_indicator_table(self.agent_name)

        for i, indicator in enumerate(indicator_list):
            color = self.random_color()  # Генерируем цвет линии
            checkbox = QCheckBox(f"{indicator} (P={self.get_period(indicator)})")
            checkbox.setChecked(True)  # По умолчанию индикатор включен
            checkbox.setStyleSheet(f"color: {color};")  # Цвет текста = цвет линии
            checkbox.stateChanged.connect(self.update_graph)

            self.indicator_checkboxes[indicator] = (checkbox, color)
            self.indicator_plots[indicator] = None  # Добавляем в список
            
            self.indicator_layout.addWidget(checkbox, i // 2, i % 2)  # Располагаем в 2 столбца
        
        self.update_graph()  # Перерисовываем график после обновления списка индикаторов

    def get_period(self, indicator_name):
        """Получает период индикатора (берем первый попавшийся из БД)"""
        data = table_for_agent.get_data_indicator_table(self.agent_name, indicator_name)
        return data[0][0] if data else "?"

    def start_updater(self):
        if not self.graph_thread.isRunning():
            self.graph_thread.running = True
            self.graph_thread.start()

    def stop_updater(self):
        if self.graph_thread.isRunning():
            self.graph_thread.running = False
            self.graph_thread.wait()

    def manual_update(self):

        data = self.graph_thread.fetch_candle_data()
        self.load_indicators()

    def update_graph(self, _=None):
        """Обновляет график с учетом индикаторов"""
        self.graph_widget.clear()  # Очищаем весь график перед отрисовкой
        graph_type = self.graph_type_selector.currentText()

        # Загружаем свечные данные
        data = table_for_agent.get_data_main_table(self.agent_name)
        if not data:
            logger.info("Нет данных для отображения.")
            QMessageBox.information(self, "Данные", "Нет данных для отображения.")
            return

        if graph_type == "Линия":
            timestamps, _, _, _, close_prices = zip(*data)
            self.graph_widget.plot(timestamps, close_prices, pen="g")

        elif graph_type == "Свечи":
            self.plot_candlestick(data)

        # Обновляем индикаторы
        self.plot_indicators()

        # Добавляем сделки
        trade_data = table_for_agent.get_data_trade_table(self.agent_name)
        self.plot_trades(trade_data)

    def plot_candlestick(self, data):
        """Рисует свечной график"""
        for i, (timestamp, open_price, high_price, low_price, close_price) in enumerate(data):
            color = "g" if close_price >= open_price else "r"
            self.graph_widget.plot([i, i], [low_price, high_price], pen=color)
            self.graph_widget.plot([i, i], [open_price, close_price], pen=pg.mkPen(color, width=4))
    
    def plot_trades(self, trade_data):
        if not trade_data:
            return

        trade_groups = {}

        # Группируем сделки по identifier
        for identifier, timestamp, price, quantity, side in trade_data:
            if identifier not in trade_groups:
                trade_groups[identifier] = []
            trade_groups[identifier].append((timestamp, price, side))

        for identifier, trades in trade_groups.items():
            trades.sort()  # Сортируем по времени
            # print(f"Identifier {identifier}: {trades}")  # Отладка

            # Рисуем точки сделок (стрелки)
            for timestamp, price, side in trades:
                color = "g" if side == "BUY" else "r"
                arrow = pg.ArrowItem(pos=(timestamp, price), angle=90 if side == "BUY" else -90, brush=color)
                self.graph_widget.addItem(arrow)

            # Логика соединения точек
            segment = []  # Текущий набор точек для соединения
            last_side = None

            for timestamp, price, side in trades:
                if not segment:
                    segment.append((timestamp, price))
                else:
                    # Продолжаем соединять, если направление одинаковое (SELL → SELL или BUY → BUY)
                    if last_side == side:
                        segment.append((timestamp, price))
                    else:
                        # Если направление сменилось, соединяем и прерываем
                        segment.append((timestamp, price))
                        x_vals, y_vals = zip(*segment)
                        # print(f"Drawing line: {segment}")  # Отладка
                        self.graph_widget.plot(x_vals, y_vals, pen=pg.mkPen("b", width=2))
                        segment = []  # Начинаем новый сегмент

                last_side = side

            # Рисуем последнюю часть линии, если остались точки
            if len(segment) > 1:
                x_vals, y_vals = zip(*segment)
                # print(f"Final line: {segment}")  # Отладка
                self.graph_widget.plot(x_vals, y_vals, pen=pg.mkPen("b", width=2))

    def plot_indicators(self):
        """Рисует индикаторы"""
        for indicator, (checkbox, color) in self.indicator_checkboxes.items():
            if checkbox.isChecked():
                if self.indicator_plots[indicator] is None:  # Только если ещё не рисовали
                    data = table_for_agent.get_data_indicator_table(self.agent_name, indicator)
                    if not data:
                        continue

                    _, timestamps, values = zip(*data)
                    self.indicator_plots[indicator] = self.graph_widget.plot(timestamps, values, pen=pg.mkPen(color, width=2))
            else:
                if self.indicator_plots[indicator]:  # Удаляем линию, если чекбокс выключен
                    self.graph_widget.removeItem(self.indicator_plots[indicator])
                    self.indicator_plots[indicator] = None

    def random_color(self):
        """Генерирует случайный цвет в формате #RRGGBB"""
        return "#{:02x}{:02x}{:02x}".format(random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))