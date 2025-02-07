import os
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTabWidget, QTextEdit, QFrame, QComboBox, 
                             QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QThread, pyqtSignal  
import pyqtgraph as pg

import paths, global_variable, gui.texts as texts
import gui.texts as texts
from core.agent.agent_manager import AgentManager
import core.table_for_agent as table_for_agent

class GraphUpdater(QThread):
    """Поток обновления графика раз в минуту"""
    data_updated = pyqtSignal(list)  # Сигнал для передачи данных в основной поток

    def __init__(self):
        super().__init__()
        self.running = True  # Флаг для работы потока

    def run(self, agent_name):
        """Запускает цикл обновления раз в 60 секунд"""
        while self.running:
            data = self.fetch_candle_data(agent_name)
            self.data_updated.emit(data)  # Отправляем данные в основной поток
            time.sleep(60)  # Обновление раз в минуту

    def fetch_candle_data(self, agent_name):
        """Загружает данные свечей из SQLite"""
        try:
            data = table_for_agent.get_data_to_graph("321")
            return data

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return []

class AgentSpecificTab(QWidget):
    def __init__(self, parent=None, agent_manager=None, agent_name=None, language=None):
        super().__init__(parent)
        self.parent = parent 
        self.agent_manager = agent_manager
        self.agent_name = agent_name
        # print("Имя агента:", self.agent_name)

        # Основной вертикальный layout
        main_layout = QVBoxLayout(self)

        # --- Блок кнопок (Старт, Стоп, Старт Бэктест) ---
        icon_size = QSize(24, 24)
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Заполняет левую часть, сдвигая кнопки вправо
        # Старт
        self.start_button = QPushButton()
        self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.start_button.setIconSize(icon_size)
        self.start_button.clicked.connect(self.start_agent)
        # Стоп
        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop.png")))
        self.stop_button.setIconSize(icon_size)
        self.stop_button.clicked.connect(self.stop_agent)
        # Бэктест
        self.backtest_button = QPushButton()
        self.backtest_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.backtest_button.setIconSize(icon_size)
        self.backtest_button.clicked.connect(lambda: self.agent_manager.backtest_agent(agent_name))
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.backtest_button)
        button_layout.addStretch()  # Заполняет пространство слева

        main_layout.addLayout(button_layout)

        # --- Вкладки (Редактор, График, Бэктест) ---
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)  # Запрещаем закрытие вкладок

        self.editor_tab = QTextEdit()
        self.tabs.addTab(self.editor_tab, "Редактор")
        self.graph_tab = QTextEdit()
        self.tabs.addTab(self.graph_tab, "График")
        self.setup_graph_tab()
        self.backtest_tab = QTextEdit()
        self.tabs.addTab(self.backtest_tab, "Бэктест")

        main_layout.addWidget(self.tabs, 3) # Вкладки занимают 3/4 окна

        # --- Окно терминала (эмуляция вывода) (1/4 высоты) ---
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: black; color: white;")
        self.terminal_output.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.terminal_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(self.terminal_output, 1)  # Терминал занимает 1/4 окна

        # Тестовый вывод в терминал
        self.print_to_terminal("Инициализация агента...")

        # Создание потока обновления
        self.graph_thread = GraphUpdater()
        self.graph_thread.data_updated.connect(self.update_graph)  # Соединяем сигнал с обновлением графика

    
    def print_to_terminal(self, text):
        """Выводит текст в эхо-терминал."""
        self.terminal_output.append(text)
    
    def setup_graph_tab(self):
        """Настраивает вкладку графика."""
        layout = QVBoxLayout(self.graph_tab)

        # Выбор типа графика
        self.graph_type_selector = QComboBox()
        self.graph_type_selector.addItems(["Линия", "Свечи"])
        self.graph_type_selector.currentIndexChanged.connect(self.manual_update)
        layout.addWidget(self.graph_type_selector)

        # Кнопка обновления
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.manual_update)
        layout.addWidget(refresh_button)

        # График
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setLabel("left", "Цена")
        self.graph_widget.setLabel("bottom", "Время")
        layout.addWidget(self.graph_widget)

    def start_agent(self):
        """Запускает агента и поток обновления графика."""
        self.agent_manager.start_agent(self.agent_name)

        if not self.graph_thread.isRunning():
            self.graph_thread.running = True
            self.graph_thread.start(self.agent_name)

    def stop_agent(self):
        """Останавливает агента и поток обновления графика."""
        self.agent_manager.stop_agent(self.agent_name)

        if self.graph_thread.isRunning():
            self.graph_thread.running = False  # Завершаем поток
            self.graph_thread.wait()  # Дожидаемся завершения
            self.print_to_terminal("Обновление графика остановлено.")

    def manual_update(self):
        """Обновляет график вручную"""
        data = self.graph_thread.fetch_candle_data(self.agent_name)
        self.update_graph(data)

    def update_graph(self, data):
        """Обновляет график из переданных данных."""
        if not data:
            self.print_to_terminal("Нет данных для графика.")
            return

        self.graph_widget.clear()
        graph_type = self.graph_type_selector.currentText()

        if graph_type == "Линия":
            timestamps, open_prices, high_prices, low_prices, close_prices = zip(*data)
            self.graph_widget.plot(timestamps, close_prices, pen="g")  # Зеленая линия

        elif graph_type == "Свечи":
            self.plot_candlestick(data)

        self.print_to_terminal("График обновлен.")

    def plot_candlestick(self, data):
        """Рисует свечной график"""
        for i, (timestamp, open_price, high_price, low_price, close_price) in enumerate(data):
            color = "g" if close_price >= open_price else "r"  # Зеленая свеча при росте, красная при падении

            # Тень свечи
            self.graph_widget.plot([i, i], [low_price, high_price], pen=color)

            # Тело свечи
            self.graph_widget.plot([i, i], [open_price, close_price], pen=pg.mkPen(color, width=4))