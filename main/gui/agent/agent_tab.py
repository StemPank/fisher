import os, pickle
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, 
                             QHeaderView, QMessageBox)
from PyQt5.QtGui import QIcon, QBrush
from PyQt5.QtCore import QSize, Qt  


import paths, global_variable, gui.texts as texts
import gui.agent.dialogs as dialogs
import core.gui.defot_file as defot_file
from core.gui.table_for_agent import Table_for_gui

from utils.logging import logger

class AgentTab(QWidget):
    def __init__(self, parent=None, language=None, agent_manager=None):
        super().__init__(parent)
        """
            Доступ через прямой доступ к родителю. 
            Это значит, что AgentTab может обратиться к атрибутам родителя
        """
        """
            parent: Ссылка на главное окно, через это получаем доступ к переменным 
                    родительского класса, его же передаем как аргумент в super().__init__ 
            QVBoxLayout: Макет для таблицы и кнопок.
            QTableWidget: Таблица с пятью колонками:
                            Скрытые заголовки.
                            Первая колонка растягивается, остальные фиксированы.
        """
        self.parent = parent  
        if language != None:
            self.language = language
        else:
            self.language = global_variable.setting_file("language")
        self.agent_manager = agent_manager

        self.layout = QVBoxLayout() 

        self.agent_table = QTableWidget()
        self.agent_table.setColumnCount(5)
        self.agent_table.setHorizontalHeaderLabels(texts.AGENT_TABLE_HEADERS[self.language])
        self.agent_table.horizontalHeader().setVisible(False)
        # Настройка поведения ширины колонок
        self.agent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # "Имя агента" растягивается
        for i in range(1, 5):  # Остальные фиксированной ширины
            self.agent_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
            self.agent_table.setColumnWidth(i, 40)  # Фиксированный размер для кнопок
        self.agent_table.horizontalHeader().setStretchLastSection(False) # Запрет изменения размеров колонок
        self.agent_table.setEditTriggers(QTableWidget.NoEditTriggers) # Запрет редактирования таблицы
        self.agent_table.cellDoubleClicked.connect(self.on_double_click) # При получении сигнала о двейном нажатии ...
        self.layout.addWidget(self.agent_table) # Добавляем таблицу на виджет

        add_agent_button = QPushButton()
        add_agent_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-plus.png")))
        add_agent_button.setIconSize(QSize(24, 24))
        # Изменяем иконку при нажатии
        add_agent_button.pressed.connect(lambda: add_agent_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-plus-pressed.png"))))
        add_agent_button.released.connect(lambda: add_agent_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-plus.png"))))
        add_agent_button.clicked.connect(self.add_agent)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_agent_button)
        
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)


    def add_agent(self):
        """
            Открывает диалоговое окно AgentDialog для ввода имени.
            Добавляет строку с кнопками управления.
        """
        logger.debug(f"Вызов диалогового окна создание агента")
        dialog = dialogs.AgentDialog(parent=self, language=self.language)
        if dialog.exec() == QDialog.Accepted:
            """
            dialog.exec()
                Возвращает значение, указывающее, как пользователь закрыл окно:
                    Если пользователь нажал кнопку "ОК" 
                        (или другую кнопку, связанную с положительным 
                        результатом), возвращается QDialog.Accepted.
                    Если пользователь нажал "Отмена" 
                        (или другую кнопку, связанную с отрицательным 
                        результатом), возвращается QDialog.Rejected.
            """
            agent_name, exchange = dialog.get_data()
            if agent_name:
                # Если имя агента уникально
                if self.is_unique_item(self.agent_table, agent_name):
                    
                    res = defot_file.New_file().create_new_file(agent_name, exchange) # Создать необходимые файлы для агента
                    
                    if res:
                        self.row_position = self.agent_table.rowCount() # rowCount() возвращает количество строк в объекте
                        self.agent_table.insertRow(self.row_position) # новая строка будет добавлена в таблицу на позицию self.row_position (индексация начинается с 0)

                        # Имя агента
                        name_item = QTableWidgetItem(agent_name)
                        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # Отключить редактирование
                        self.agent_table.setItem(self.row_position, 0, name_item) # Устанавливаем данные в новую строку

                        # Кнопки управления
                        self.add_table_buttons(self.row_position, agent_name)

    def is_unique_item(self, table_widget, text, column=0):
        """
        Проверяет, существует ли элемент с заданным текстом в указанной колонке таблицы.
        
        :param table_widget: QTableWidget - таблица для проверки
        :param text: str - текст для проверки на уникальность
        :param column: int - индекс колонки для проверки (по умолчанию 0)
        :return: (bool) - True, если текст уникален, False, если он уже есть в таблице
        """
        for row in range(table_widget.rowCount()):
            item = table_widget.item(row, column)
            if item and item.text() == text:
                logger.info("Агент с атким именем уже существует")
                QMessageBox.information(self, "Ошибка", "Агент с атким именем уже существует")
                return False  # Найден дубликат
        return True  # Уникально

    def add_table_buttons(self, row, agent_name):
        """
            Кнопки "Старт", "Стоп", "Настройки", "Удалить"

            :row (int) - позиция, строка в таблице
            :agent_name (str) - название агента
        """
        icon_size = QSize(24, 24)

        # Кнопка "Старт"
        self.start_button = QPushButton()
        self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))
        self.start_button.setIconSize(icon_size)
        self.start_button.clicked.connect(lambda: self.start_agent(agent_name))
        self.agent_table.setCellWidget(row, 1, self.start_button)

        # Кнопка "Стоп"
        stop_button = QPushButton()
        stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop.png")))
        stop_button.setIconSize(icon_size)
        # Изменяем иконку при нажатии
        stop_button.pressed.connect(lambda: stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop-pressed.png"))))
        stop_button.released.connect(lambda: stop_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-stop.png"))))
        stop_button.clicked.connect(lambda: self.stop_agent(agent_name))
        self.agent_table.setCellWidget(row, 2, stop_button)

        # Кнопка "Настройки"
        settings_button = QPushButton()
        settings_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-settings.png")))
        settings_button.setIconSize(icon_size)
        # Изменяем иконку при нажатии
        settings_button.pressed.connect(lambda: settings_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-settings-pressed.png"))))
        settings_button.released.connect(lambda: settings_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-settings.png"))))
        settings_button.clicked.connect(lambda: self.open_settings(agent_name))
        self.agent_table.setCellWidget(row, 3, settings_button)
        

        # Кнопка "Удалить"
        delete_button = QPushButton()
        delete_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-trash.png")))
        delete_button.setIconSize(icon_size)
        # Изменяем иконку при нажатии
        delete_button.pressed.connect(lambda: delete_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-trash-pressed.png"))))
        delete_button.released.connect(lambda: delete_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-trash.png"))))
        delete_button.clicked.connect(lambda: self.remove_agent(row, agent_name))
        self.agent_table.setCellWidget(row, 4, delete_button)

    
    def start_agent(self, agent_name):
        """
            Запускает агента.

            :agent_name (str) - имя агента
        """
        logger.debug(f"Нажата кнопка запуска агента {agent_name}")
        self.table_agent = Table_for_gui(agent_name, global_variable.setting_file("folder_path"))
        row = self.table_agent.get_data_main_table()
        if row == []:
            logger.error(f"Параметры агента не настроены (Зайдите в агента и сохраните начальные параметры)")
            return
        variables = self.table_agent.get_all_variables()
        logger.debug(f"Переданные параметры {(row[0][0], row[0][1], row[0][2], row[0][3])} переменные {variables}")
        res = self.agent_manager.start_agent(agent_name, 
                                             row[0][0], 
                                             row[0][1], 
                                             row[0][2],  
                                             row[0][3], 
                                             variables)
        if res:
            self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play-pressed.png")))
    
    def stop_agent(self, agent_name):
        """
            Останавливает агента.

            :agent_name (str) - имя агента
        """
        logger.debug(f"Нажата кнопка остановки агента {agent_name}")
        res = self.agent_manager.stop_agent(agent_name)
        if res:
            self.start_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-play.png")))

    def open_settings(self, agent_name):
        """
            Открытет диалоговое окно настроек агента

            :agent_name (str) - имя агента
        """
        logger.debug(f"Нажата кнопка настроек агента {agent_name}")
        dialog = dialogs.SettingsDialog(self, agent_name, self.language)
        logger.debug(f"Открыто окно настроек агента {agent_name}")
        dialog.exec()
    
    def remove_agent(self, row, agent_name):
        """
            Удаляет агента и его файлов

            :agent_name (str) - имя агента
        """
        logger.debug(f"Нажата кнопка удаления агента {agent_name}")
        defot_file.New_file().del_file_agent(agent_name)
        self.agent_table.removeRow(row)
        logger.debug(f"Агент удален {agent_name}")

    def on_double_click(self, row, column):
        """
            Обработчик двойного клика по таблице агентов.
            
            :row (int) - позиция, строка в таблице
            :column (int) - столбец таблицы, должен быть 1
        """
        if column == 0:  # Открываем вкладку только при клике по имени агента
            agent_name = self.agent_table.item(row, column).text()
            logger.debug(f"Было двойное нажатие по агенту {agent_name}")
            self.parent.open_agent_tab(agent_name)


    def save_state(self):
        """
            Сохранение состояния
            :return: dict - состояние таблицы агентов
        """
        agents_state = []

        for row in range(self.agent_table.rowCount()):
            # Получаем имя агента
            agent_name = self.agent_table.item(row, 0).text()

            # Проверяем, существует ли соответствующая папка
            folder_path = os.path.join(global_variable.setting_file("folder_path"), agent_name)
            folder_exists = os.path.isdir(folder_path) # логическое значение, указывающее, существует ли папка агента.

            # Сохраняем состояние агента в список
            agents_state.append({
                "name": agent_name,
                "folder_exists": folder_exists
            })

        return {"agents": agents_state}

    def load_state(self, state):
        """
            Загружает список агентов в таблицу из сохраненного состояния.
            Помечает отсутствующие папки серым и отключает кнопки.
            :param state: dict - сохраненное состояние
        """

        self.agent_table.setRowCount(0)
        agents = state.get("agents", [])
        base_folder_path = global_variable.setting_file("folder_path")

        for agent in agents:
            # Проверяем, существует ли соответствующая папка
            agent_name = agent.get("name")
            folder_path = os.path.join(base_folder_path, agent_name)
            folder_exists = os.path.isdir(folder_path) # логическое значение, указывающее, существует ли папка агента.

            # Добавляем строку в таблицу
            row_position = self.agent_table.rowCount()
            self.agent_table.insertRow(row_position)

            # Имя агента
            name_item = QTableWidgetItem(agent_name)
            if not folder_exists:
                name_item.setForeground(QBrush(Qt.gray))  # Устанавливаем серый цвет
            self.agent_table.setItem(row_position, 0, name_item)

            # Добавляем кнопки управления
            self.add_table_buttons(row_position, agent_name)

            # Отключаем кнопки управления(кроме удаления), если папка агента отсутствует
            if not folder_exists:
                for column in range(1, 4):  # Столбцы с кнопками
                    widget = self.agent_table.cellWidget(row_position, column)
                    if widget:
                        widget.setEnabled(False)



def start_agent_from_bot(agent_name):
    """
        Запускает агента.

        :agent_name (str) - имя агента
    """
    logger.debug(f"Запуска агента {agent_name} по команде из телеграмм бота")
    from core.gui.agent_manager import AgentManager
    agent_manager = AgentManager()
    table_agent = Table_for_gui(agent_name, global_variable.setting_file("folder_path"))
    row = table_agent.get_data_main_table()
    if row == []:
        logger.error(f"Параметры агента не настроены (Зайдите в агента и сохраните начальные параметры)")
        return False
    variables = table_agent.get_all_variables()
    logger.debug(f"Переданные параметры {(row[0][0], row[0][1], row[0][2], row[0][3])} переменные {variables}")
    res = agent_manager.start_agent(agent_name, 
                                        row[0][0], 
                                        row[0][1], 
                                        row[0][2],  
                                        row[0][3], 
                                        variables)

def stop_agent_from_bot(agent_name):
        """
            Останавливает агента.

            :agent_name (str) - имя агента
        """
        logger.debug(f"Остановка агента {agent_name} по команде из телеграмм бота")
        from core.gui.agent_manager import AgentManager
        agent_manager = AgentManager()
        res = agent_manager.stop_agent(agent_name)

def get_list_agent():
    try:
        if not os.path.exists(paths.AGENT_REPOSITORY):
            return False
        agent_folders = [folder for folder in os.listdir(paths.AGENT_REPOSITORY) if os.path.isdir(os.path.join(paths.AGENT_REPOSITORY, folder))]
        return agent_folders
    except:
        return False