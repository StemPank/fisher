import os
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTabWidget, QLabel, QLineEdit, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize  

import paths, global_variable, gui.texts as texts
from core.gui.agent_manager import AgentManager
from core.gui.table_for_agent import Table_for_gui
from gui.agent.editor_tab import EditorTab
from gui.agent.graph_tab import GraphTab
from gui.agent.backtest_tab import BacktestEditor
from gui.agent.optimization_tab import OptimizationTab
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

        self.table_agent = Table_for_gui(self.agent_name, global_variable.setting_file("folder_path"))

        # Основной вертикальный layout
        main_layout = QVBoxLayout(self)

        # --- Блок кнопок (Старт, Стоп, Бэктест) ---
        icon_size = QSize(24, 24)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.start_button = QPushButton()
        self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.start_button.setIconSize(icon_size)
        self.start_button.setToolTip("Запуск агента в реальном времени")
        self.start_button.setToolTipDuration(2000)
        self.start_button.pressed.connect(lambda: self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play-pressed.png"))))
        self.start_button.released.connect(lambda: self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png"))))
        self.start_button.clicked.connect(self.start_agent)

        self.backtest_button = QPushButton()
        self.backtest_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.backtest_button.setIconSize(icon_size)
        self.backtest_button.setToolTip("Запуск агента в режиме бэктеста")
        self.backtest_button.setToolTipDuration(2000)
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
        self.start_save_button.hide() # Кнопка скрыта, удалить за ненадобностью

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop.png")))
        self.stop_button.setIconSize(icon_size)
        self.stop_button.setToolTip("Остановка агента")
        self.stop_button.setToolTipDuration(2000)
        self.stop_button.pressed.connect(lambda: self.stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop-pressed.png"))))
        self.stop_button.released.connect(lambda: self.stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop.png"))))
        self.stop_button.clicked.connect(self.stop_agent)

        self.optimization_button = QPushButton()
        self.optimization_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.optimization_button.setIconSize(icon_size)
        self.optimization_button.setToolTip("Запуск агента в режиме оптимизации")
        self.optimization_button.setToolTipDuration(2000)
        self.optimization_button.pressed.connect(lambda: self.optimization_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play-pressed.png"))))
        self.optimization_button.released.connect(lambda: self.optimization_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png"))))
        self.optimization_button.clicked.connect(self.optimization_agent_backtest)
        self.optimization_button.hide() # Кнопка скрыта, удалить за ненадобностью
        
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

        self.editor_tab = EditorTab(self.agent_name, self.table_agent, self.language)
        self.tabs.addTab(self.editor_tab, texts.TAB_AGENTA[self.language][0])

        self.graph_tab = GraphTab(self.agent_name, self.language)
        self.tabs.addTab(self.graph_tab, texts.TAB_AGENTA[self.language][1])

        self.backtest_tab = BacktestEditor(self.agent_name)
        self.tabs.addTab(self.backtest_tab, texts.TAB_AGENTA[self.language][2])
        
        self.optimization_tab = OptimizationTab(self, self.agent_name, self.table_agent, self.agent_manager, self.language)
        self.tabs.addTab(self.optimization_tab, texts.TAB_AGENTA[self.language][3])
        
        main_layout.addWidget(self.tabs)
    
    def start_agent(self):
        """Запускает агента."""
        logger.debug(f"Нажата кнопка запуска агента {self.agent_name}")
        logger.warning("Тастовый")
        variables = []
        for i in range(1, self.editor_tab.variables_layout.count(), 3):  # Начинаем с 1, чтобы пропустить кнопку добавления переменной
            variable_label = self.editor_tab.variables_layout.itemAt(i).widget()  # Каждая пара: Label и QLineEdit
            variable_input = self.editor_tab.variables_layout.itemAt(i+1).widget()

            if isinstance(variable_label, QLabel) and isinstance(variable_input, QLineEdit):
                variable_name = variable_label.text()
                variable_value = variable_input.text()
                # Добавляем переменную в список
                variables.append((variable_name, int(float(variable_value))))
        if self.editor_tab.commission_input.text() == '':
            logger.error(f"Параметры агента не настроены")
            QMessageBox.warning(self, "Ошибка", "На вкладке 'Редактор' введите комиссию и нажмите сохранить")
            return
        logger.debug(f"Переданные параметры {(self.editor_tab.pair_label.text(), self.editor_tab.pair_combo.currentText(), 
                                              self.editor_tab.interval_input.currentText(), self.editor_tab.commission_input.text())} переменные {variables}")
        res = self.agent_manager.start_agent(self.agent_name, 
                                             self.editor_tab.pair_label.text(), 
                                             self.editor_tab.pair_combo.currentText(), 
                                             self.editor_tab.interval_input.currentText(), 
                                             self.editor_tab.commission_input.text(), 
                                             variables)
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
        variables = []
        for i in range(1, self.editor_tab.variables_layout.count(), 3):  # Начинаем с 1, чтобы пропустить кнопку добавления переменной
            variable_label = self.editor_tab.variables_layout.itemAt(i).widget()  # Каждая пара: Label и QLineEdit
            variable_input = self.editor_tab.variables_layout.itemAt(i+1).widget()
            if isinstance(variable_label, QLabel) and isinstance(variable_input, QLineEdit):
                variable_name = variable_label.text()
                variable_value = variable_input.text()
                variables.append((variable_name, int(float(variable_value))))
        if self.editor_tab.commission_input.text() == '':
            logger.error(f"Параметры агента не настроены")
            QMessageBox.warning(self, "Ошибка", "На вкладке 'Редактор' введите комиссию и нажмите сохранить")
            return
        logger.debug(f"Переданные {(self.editor_tab.pair_label.text(), self.editor_tab.pair_combo.currentText(), 
                                              self.editor_tab.interval_input.currentText(), self.editor_tab.commission_input.text())} переменные {variables}")
        self.agent_manager.start_agent_backtest(self.agent_name, 
                                             self.editor_tab.pair_label.text(), 
                                             self.editor_tab.pair_combo.currentText(), 
                                             self.editor_tab.interval_input.currentText(), 
                                             self.editor_tab.commission_input.text(), 
                                             variables)
    
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
        self.results_tab = ResultsTab(self.agent_name)
        self.tabs.addTab(self.results_tab, texts.TAB_AGENTA[self.language][4])
    
    