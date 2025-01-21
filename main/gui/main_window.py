import sys, os, pickle
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenuBar, QMenu, QAction, 
                            QTabWidget, QWidget, QVBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon
from gui.agent.agent_tab import AgentTab
from gui.setting.setting_tab import SettingTab
from gui.agent.agent_specific_tab import AgentSpecificTab
from gui.defot_file import create_defolt_file_setting
import gui.global_variable as global_variable
import gui.texts as texts

class MainWindow(QMainWindow):
    def __init__(self):
        #вызывает метод init() родительского класса с аргументами и ключевыми аргументами, переданными конструктору дочернего класса
        super().__init__() 
        """
            setWindowTitle и setGeometry: Установка заголовка и размеров окна.
            init_ui: Создание интерфейса.
            load_state: Загрузка состояния.
        """
        # создание дефолтного файла настроек приложения
        create_defolt_file_setting() 
        
        self.setWindowTitle("Fisher")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()
        self.load_state()
        

    # Создание основных элементов:
    def init_ui(self):
        # Меню бар
        menu_bar = QMenuBar() # определяем виджет
        self.setMenuBar(menu_bar)

        # Меню "Инструменты"
        tools_menu = QMenu(texts.MENU_TOOLS[global_variable.language_check()], self)
        menu_bar.addMenu(tools_menu)

        self.agent_action = QAction(texts.MENU_AGENTS[global_variable.language_check()], self, checkable=True)
        self.agent_action.toggled.connect(self.all_tab) # нужно проверить нажатие в вызываемом методе
        tools_menu.addAction(self.agent_action)

        self.setting_action = QAction(texts.MENU_SETTINGS[global_variable.language_check()], self, checkable=True)
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

    def all_tab(self, checked):
        """
        Создать или удалить вкладки меню
        """
        action = self.sender() # Получаем действие, вызвавшее событие
        if checked:
            self.add_tab(action.text())
        else:
            self.remove_tab(action.text())

    def add_tab(self, tab_name):
        """
        Создать вкладку 

        :param tab_name: str имя кнопки меню
        """
        # Проверяем, существует ли уже вкладка с таким именем
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                return  # Если вкладка есть, ничего не делаем

        # Создаём новую вкладку
        if tab_name == texts.MENU_AGENTS[global_variable.language_check()]:
            self.agent_tab = AgentTab(self)

            # Загружаем состояние только если вкладка открывается впервые
            # if not hasattr(self, "agent_tab_loaded"):
            #     self.agent_tab_loaded = True
                # Если файл состояния существует, загружаем состояние
            if os.path.exists(global_variable.OPERATIVE_STATE_FILE):
                with open(global_variable.OPERATIVE_STATE_FILE, "rb") as file:
                    state = pickle.load(file)
                    self.agent_tab.load_state(state)

            self.tabs.addTab(self.agent_tab, tab_name)

        elif tab_name == texts.MENU_SETTINGS[global_variable.language_check()]:
            self.setting_tabs = SettingTab(self)
            self.tabs.addTab(self.setting_tabs, tab_name)
        else:
            # Для динамических вкладок
            new_tab = AgentSpecificTab(self, tab_name)
            self.tabs.addTab(new_tab, tab_name)

    def remove_tab(self, tab_name):
        """
        Удалить вкладку 

        :param tab_name: str имя кнопки меню
        """
        # Находим вкладку с указанным именем и удаляем её
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_name:
                self.tabs.removeTab(i)
                break

    def close_tab(self, index):
        """
            Закрывает вкладку. Если вкладка создана из меню, снимается галочка.
            Сохраняет состояние вкладки агентов перед закрытием.

            :param index: int индекс вкладки
        """
        widget = self.tabs.widget(index)
        try:
            if widget == self.agent_tab:
                self.agent_action.setChecked(False)
                # Сохраняем состояние вкладки агентов в файл
                state = self.agent_tab.save_state()
                with open(global_variable.OPERATIVE_STATE_FILE, "wb") as file:
                    pickle.dump(state, file)

                self.agent_tab.deleteLater()  # Удаляем виджет из памяти
                del self.agent_tab  # Удаляем ссылку
                return
        except: pass
        try:
            if widget == self.setting_tabs:
                self.setting_action.setChecked(False)
                return
        except: pass
        if widget:
            self.tabs.removeTab(index)
    
    def open_agent_tab(self, agent_name):
        """
            Открывает новую вкладку с агентом.
        
            :param agent_name: str имя агента
        """
        # Создаем новую вкладку
        self.agent_specific_tab = AgentSpecificTab(self, agent_name)
        # Добавляем вкладку в QTabWidget главного окна
        self.tabs.addTab(self.agent_specific_tab, agent_name)
        self.tabs.setCurrentWidget(self.agent_specific_tab)
    
    
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
        
        with open(global_variable.STATE_FILE, "wb") as file:
            pickle.dump(state, file)

    def load_state(self):
        """
            Загрузка состояния
        """
        # Проверяем, существует ли файл состояния
        if os.path.exists(global_variable.STATE_FILE):
            with open(global_variable.STATE_FILE, "rb") as file:
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
            if texts.MENU_AGENTS[global_variable.language_check()] in open_tabs:
                self.agent_tab.load_state(state.get("agent_tab_state", {}))
                
                
                # if tab_name == texts.MENU_AGENTS[global_variable.language_check()]:
                #     self.agent_action.setChecked(True)
                #     if "agent_tab_state" in state and hasattr(self, "agent_tab"):
                #         self.agent_tab.load_state(state["agent_tab_state"])  # Восстанавливаем состояние AgentTab
                # elif tab_name == texts.MENU_SETTINGS[global_variable.language_check()]:
                #     self.setting_action.setChecked(True)
                # else:
                #     self.add_tab(tab_name)

            # Загружаем дополнительные вкладки, если есть
            # for tab_name in open_tabs:
            #     if tab_name not in (texts.MENU_AGENTS[global_variable.language_check()], texts.MENU_SETTINGS[global_variable.language_check()]):
            #         self.add_tab(tab_name)

    def closeEvent(self, event):
        """
            Действия при закрятии приложения
        """
        self.save_state()
        AgentTab().save_state()
        super().closeEvent(event)