import sys, os, pickle
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu, QAction, 
                            QTabWidget, QWidget, QVBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon

import paths, global_variable, gui.texts as texts

from utils.logging import logger

from gui.agent.agent_tab import AgentTab
from gui.agent.agent_specific_tab import AgentSpecificTab
from gui.setting.provider_tab import ProviderTab
from gui.setting.setting_tab import SettingTab

from core.gui.agent_manager import AgentManager

class MainWindow(QMainWindow):
    def __init__(self):
        """
            Определяет глобальные элементы, вызывает создание интерфейса
        """
        #вызывает метод init() родительского класса с аргументами и ключевыми аргументами, переданными конструктору дочернего класса
        super().__init__() 
        
        # setWindowTitle и setGeometry: Установка заголовка и размеров окна
        self.setWindowTitle("Fisher")
        self.setGeometry(100, 100, 800, 600)

        self.language = global_variable.setting_file("language") or "russian"

        self.init_ui() # init_ui: Создание интерфейса
        self.load_state() # load_state: Загрузка состояния
        
    # Создание основных элементов:
    def init_ui(self):
        """
            Создает интерфейс
        """
        # Меню бар
        menu_bar = QMenuBar() # определяем виджет
        self.setMenuBar(menu_bar)

        # Меню "Инструменты"
        tools_menu = QMenu(texts.MENU_TOOLS[self.language], self)
        menu_bar.addMenu(tools_menu)

        # Вкладка Агенты
        self.agent_action = QAction(texts.MENU_AGENTS[self.language], self, checkable=True)
        self.agent_action.toggled.connect(self.all_tab) # нужно проверить нажатие в вызываемом методе
        tools_menu.addAction(self.agent_action)

        # Вкладка Поставщики данных
        self.provider_action = QAction(texts.MENU_PROVIDERS[self.language], self, checkable=True)
        self.provider_action.toggled.connect(self.all_tab)
        tools_menu.addAction(self.provider_action)

        # Вкладка Настройки
        self.setting_action = QAction(texts.MENU_SETTINGS[self.language], self, checkable=True)
        self.setting_action.toggled.connect(self.all_tab)
        tools_menu.addAction(self.setting_action)

        # Меню "Действия"
        # actions_menu = QMenu("Действия", self)
        # menu_bar.addMenu(actions_menu)

        # Центральный виджет
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True) # на каждой вкладке появляется кнопка закрытия. Когда кнопка закрытия нажата, QTabWidget излучает сигнал tabCloseRequested
        self.tabs.tabCloseRequested.connect(self.close_tab) # Подключить сигнал tabCloseRequested к close_tab
        self.setCentralWidget(self.tabs)

        self.agent_manager = AgentManager()

    def all_tab(self, checked):
        """
        Создать или удалить вкладки меню

        :checked - информация о кнопки из меню, активна или нет
        """
        action = self.sender() # Получаем действие, вызвавшее событие
        logger.debug(f"Нажатие вкладки меню: {action.text()} {checked}")
        if checked:
            self.add_tab(action.text())
        else:
            self.remove_tab(action.text())

    def add_tab(self, tab_name):
        """
        Создать вкладку 

        :tab_name - (str) имя кнопки меню
        """
        # Проверяем, существует ли уже вкладка с таким именем
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                return  # Если вкладка есть, ничего не делаем

        # Создаём новую вкладку
        if tab_name == texts.MENU_AGENTS[self.language]:
            self.agent_tab = AgentTab(self, self.language, self.agent_manager)

            # Загружаем состояние только если есть файл состояния
            if os.path.exists(paths.OPERATIVE_STATE_FILE):
                with open(paths.OPERATIVE_STATE_FILE, "rb") as file:
                    state = pickle.load(file)
                    self.agent_tab.load_state(state)

            self.tabs.addTab(self.agent_tab, tab_name)

        elif tab_name == texts.MENU_PROVIDERS[self.language]:
            self.provider_tab = ProviderTab(self, self.language)
            self.tabs.addTab(self.provider_tab, tab_name)

        elif tab_name == texts.MENU_SETTINGS[self.language]:
            self.setting_tabs = SettingTab(self, self.language)
            self.tabs.addTab(self.setting_tabs, tab_name)
        
        else:
            # Для динамических вкладок
            new_tab = AgentSpecificTab(self, self.agent_manager, tab_name, self.language)
            self.tabs.addTab(new_tab, tab_name)
            
        logger.debug(f"Открыта вкладка: {tab_name}")

    def remove_tab(self, tab_name):
        """
        Если срабатывает из меню то галочка уберается атоматом и 
        закрывается вкладка по индексу

        :tab_name - (str) имя кнопки меню
        """
        # Находим вкладку с указанным именем и удаляем её
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                self.tabs.removeTab(i)
                logger.debug(f"Закрыта вкладка: {tab_name}")
                break

    def close_tab(self, index):
        """
            Закрывает вкладку. Если вкладка создана из меню, снимается галочка.
            Сохраняет состояние вкладки агентов перед закрытием.

            :index - (int) индекс вкладки
        """
        widget = self.tabs.widget(index)
        # logger.debug(f"Закрытие вкладки: {widget}")

        # Проверяет наличие атрибута перед его использованием
        if hasattr(self, "agent_tab") and widget == self.agent_tab:
            self.agent_action.setChecked(False)
            
            # Сохраняем состояние вкладки агентов в файл
            state = self.agent_tab.save_state()
            with open(paths.OPERATIVE_STATE_FILE, "wb") as file:
                pickle.dump(state, file)

            self.agent_tab.deleteLater()  # Удаляем виджет из памяти
            del self.agent_tab  # Удаляем ссылку
            return
        if hasattr(self, "provider_tab") and widget == self.provider_tab:
            self.provider_action.setChecked(False)
            return
        if hasattr(self, "setting_tabs") and widget == self.setting_tabs:
            self.setting_action.setChecked(False)
            return
        
        # Передает для закрытия по индексу
        if widget:
            self.tabs.removeTab(index)
            logger.debug(f"Закрыта вкладка: {self.tabs.tabText(index)}")
    
    def open_agent_tab(self, agent_name):
        """
            Открывает новую вкладку с агентом.
        
            :agent_name - (str) имя агента
        """
        # Создаем новую вкладку
        self.agent_specific_tab = AgentSpecificTab(self, self.agent_manager, agent_name, self.language)
        # Добавляем вкладку в QTabWidget главного окна
        self.tabs.addTab(self.agent_specific_tab, agent_name)
        self.tabs.setCurrentWidget(self.agent_specific_tab)
        
        logger.debug(f"Открыта вкладка агента: {agent_name}")
    
    
    def save_state(self):
        """
            Сохранение состояния
        """
        # state = {
        #     "agent_tab_state": self.agent_tab.save_state() if hasattr(self, "agent_tab") else None,
        #     "open_tabs": [self.tabs.tabText(i) for i in range(self.tabs.count())],
        # }

        # Собираем список открытых вкладок
        open_tabs = [self.tabs.tabText(i) for i in range(self.tabs.count())]

        # Сохраняем состояние вкладки AgentTab, если она существует
        agent_tab_state = None
        if hasattr(self, "agent_tab"):
            agent_tab_state = self.agent_tab.save_state()
        
        state = {
            "open_tabs": open_tabs,
            "agent_tab_state": agent_tab_state,
            "window_geometry": self.saveGeometry(),  # Сохраняем размеры и положение окна
            "window_state": self.saveState()         # Сохраняем состояние окна (например, меню)
        }
        
        with open(paths.STATE_FILE, "wb") as file:
            pickle.dump(state, file)

    def load_state(self):
        """
            Загрузка состояния
        """
        # Проверяем, существует ли файл состояния
        if os.path.exists(paths.STATE_FILE):
            with open(paths.STATE_FILE, "rb") as file:
                state = pickle.load(file)

            # Восстанавливаем размеры и положение окна
            if "window_geometry" in state:
                self.restoreGeometry(state["window_geometry"])
            if "window_state" in state:
                self.restoreState(state["window_state"])

            # Загружаем вкладки, которые были открыты перед закрытием
            open_tabs = state.get("open_tabs", [])
            for tab_name in open_tabs:
                self.add_tab(tab_name)

            # Если вкладка "Агенты" была открыта, загружаем её состояние
            if texts.MENU_AGENTS[self.language] in open_tabs:
                self.agent_tab.load_state(state.get("agent_tab_state", {}))
                
                if tab_name == texts.MENU_AGENTS[self.language]:
                    self.agent_action.setChecked(True)
                    if "agent_tab_state" in state and hasattr(self, "agent_tab"):
                        self.agent_tab.load_state(state["agent_tab_state"])  # Восстанавливаем состояние AgentTab

                elif tab_name == texts.MENU_PROVIDERS[self.language]:
                    self.provider_action.setChecked(True)

                elif tab_name == texts.MENU_SETTINGS[self.language]:
                    self.setting_action.setChecked(True)

                else:
                    self.add_tab(tab_name)

            # Загружаем дополнительные вкладки, если есть
            for tab_name in open_tabs:
                if tab_name not in (texts.MENU_AGENTS[self.language], texts.MENU_SETTINGS[self.language]):
                    self.add_tab(tab_name)

    def closeEvent(self, event):
        """
            Действия при закрятии приложения
        """
        self.save_state()
        logger.info("Приложение остановлено")
        AgentTab().save_state()
        super().closeEvent(event)