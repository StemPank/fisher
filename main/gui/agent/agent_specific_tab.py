import os
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTabWidget, QTextEdit, QFrame, QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize  

import paths, global_variable, gui.texts as texts
from core.gui.agent_manager import AgentManager
from gui.agent.editor_tab import EditorTab
from gui.agent.graph_tab import GraphTab
from gui.agent.backtest_tab import BacktestEditor
from gui.agent.result_tab import ResultsTab


from utils.logging import logger

class AgentSpecificTab(QWidget):
    def __init__(self, parent=None, agent_manager=None, agent_name=None, language=None):
        super().__init__(parent)
        self.parent = parent 
        self.agent_manager = agent_manager
        self.agent_name = agent_name
        if language != None:
            self.language = language
        else:
            self.language = global_variable.setting_file("language")

        # Основной вертикальный layout
        main_layout = QVBoxLayout(self)

        # --- Блок кнопок (Старт, Стоп, Бэктест) ---
        icon_size = QSize(24, 24)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.start_button = QPushButton()
        self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.start_button.setIconSize(icon_size)
        self.start_button.clicked.connect(self.start_agent)

        self.backtest_button = QPushButton()
        self.backtest_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.backtest_button.setIconSize(icon_size)
        # Изменяем иконку при нажатии
        self.backtest_button.pressed.connect(lambda: self.backtest_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play-pressed.png"))))
        self.backtest_button.released.connect(lambda: self.backtest_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png"))))
        self.backtest_button.clicked.connect(self.start_agent_backtest)
        
        self.start_save_button = QPushButton()
        self.start_save_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-font-disk.png")))
        self.start_save_button.setIconSize(icon_size)
        # Изменяем иконку при нажатии
        self.start_save_button.pressed.connect(lambda: self.start_save_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-font-disk-pressed.png"))))
        self.start_save_button.released.connect(lambda: self.start_save_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-font-disk.png"))))
        self.start_save_button.clicked.connect(self.save_and_start_agent)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop.png")))
        self.stop_button.setIconSize(icon_size)
        # Изменяем иконку при нажатии
        self.stop_button.pressed.connect(lambda: self.stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop-pressed.png"))))
        self.stop_button.released.connect(lambda: self.stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop.png"))))
        self.stop_button.clicked.connect(self.stop_agent)

        self.optimization_button = QPushButton()
        self.optimization_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.optimization_button.setIconSize(icon_size)
        # Изменяем иконку при нажатии
        self.optimization_button.pressed.connect(lambda: self.optimization_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play-pressed.png"))))
        self.optimization_button.released.connect(lambda: self.optimization_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png"))))
        self.optimization_button.clicked.connect(self.optimization_agent_backtest)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.backtest_button)
        button_layout.addWidget(self.start_save_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.optimization_button)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # --- Вкладки (Редактор, График, Бэктест) ---
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)

        self.editor_tab = EditorTab(self.agent_name)
        self.tabs.addTab(self.editor_tab, texts.TAB_AGENTA[self.language][0])

        self.graph_tab = GraphTab(self.agent_name, self.language)
        self.tabs.addTab(self.graph_tab, texts.TAB_AGENTA[self.language][1])

        self.backtest_tab = BacktestEditor(self.agent_name)
        self.tabs.addTab(self.backtest_tab, texts.TAB_AGENTA[self.language][2])
        
        main_layout.addWidget(self.tabs)
        # main_layout.addWidget(self.tabs, 3)

        # --- Окно терминала ---
        # self.terminal_output = QTextEdit()
        # self.terminal_output.setReadOnly(True)
        # self.terminal_output.setStyleSheet("background-color: black; color: white;")
        # self.terminal_output.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        # self.terminal_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # main_layout.addWidget(self.terminal_output, 1)
        # self.print_to_terminal("Инициализация агента...")

    # def print_to_terminal(self, text):
    #     """Выводит текст в терминал."""
    #     self.terminal_output.append(text)
    
    def start_agent(self):
        """Запускает агента."""
        logger.debug(f"Нажата кнопка запуска агента {self.agent_name}")
        res = self.agent_manager.start_agent(self.agent_name)
        if res:
            self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play-pressed.png")))
        

    def save_and_start_agent(self):
        """Запускает агента."""
        logger.debug(f"Нажата кнопка сохранения файла {self.agent_name}")
        self.editor_tab.save_file()  # Сохраняем файл перед запуском
        # self.agent_manager.start_agent(self.agent_name)

    def start_agent_backtest(self):
        """
            Запускает агента.
        
            это применение торговой стратегии к историческим данным для оценки ее прибыльности и возможных рисков
        """
        logger.debug(f"Нажата кнопка запуска агента {self.agent_name} в режиме backtest")
        self.agent_manager.start_agent_backtest(self.agent_name)
    
    def stop_agent(self):
        """Останавливает агента."""
        logger.debug(f"Нажата кнопка остановки агента {self.agent_name}")
        res = self.agent_manager.stop_agent(self.agent_name)
        if res:
            self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))

    def optimization_agent_backtest(self):
        """
            Запускает оптимизацию агента.
        """
        logger.debug(f"Нажата кнопка запуска оптимизации агента {self.agent_name} в режиме backtest")
        self.agent_manager.optimization_agent_backtest(self.agent_name)
        # Создаём вкладку с результатами
        self.results_tab = ResultsTab(self.agent_name)
        self.tabs.addTab(self.results_tab, texts.TAB_AGENTA[self.language][3])
    
    
    # def start_agent(self):
    #     """Запускает агента."""
    #     self.editor_tab.save_file()  # Сохраняем файл перед запуском
    #     self.print_to_terminal("Запуск агента")
    #     self.agent_manager.start_agent(self.agent_name, self.print_to_terminal)
    #     self.graph_tab.start_updater()
    
    # def stop_agent(self):
    #     """Останавливает агента."""
    #     self.print_to_terminal("Остановка агента")
    #     self.agent_manager.stop_agent(self.agent_name, self.print_to_terminal)
    #     self.graph_tab.stop_updater()
