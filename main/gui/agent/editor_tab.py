import os
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QComboBox, QLineEdit, QLabel, QMessageBox, QToolButton, QToolTip, QScrollArea, QSizePolicy
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtGui import QFont, QColor, QIntValidator
from PyQt5.QtCore import Qt

import paths, global_variable, config, gui.texts as text

from utils.logging import logger

class AdvancedEditor(QsciScintilla):
    def __init__(self):
        super().__init__()

        # Подсветка синтаксиса Python
        self.lexer = QsciLexerPython()
        self.lexer.setDefaultFont(QFont("Courier", 12))
        self.setLexer(self.lexer)

        # Настройки нумерации строк
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, "0000")  # Автоопределение ширины номеров строк
        self.setMarginsForegroundColor(QColor("#555"))
        self.setMarginsBackgroundColor(QColor("#EEE"))

        # Автоотступы
        self.setAutoIndent(True)

        # Подсветка текущей строки
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#E0E0E0"))

        # Скобочное выделение
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Сворачивание кода
        self.setFolding(QsciScintilla.PlainFoldStyle)

        # Прокрутка
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

class EditorTab(QWidget):
    """Редактор кода с настройками монетной пары, интервала и комиссии"""

    def __init__(self, agent_name, table_agent, language):
        super().__init__()
        self.agent_name = agent_name
        self.table_agent = table_agent
        self.language = language
        self.file_path = f"{global_variable.setting_file('folder_path')}/{agent_name}/run_{agent_name}.py"
        self.layout = QVBoxLayout(self)
        
        # Верхняя панель с кнопками "Сохранить" и "Загрузить"
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(text.EDITOR_SETTING[self.language][0])
        self.load_button = QPushButton(text.EDITOR_SETTING[self.language][1])

        self.save_button.clicked.connect(self.save_all)
        self.load_button.clicked.connect(self.load_all)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        self.layout.addLayout(button_layout)

        # Панель настроек (Монетная пара, Интервал, Комиссия)
        settings_layout = QHBoxLayout()

        # Монетная пара
        self.pair_label = QLabel(text.EDITOR_SETTING[self.language][2])
        self.pair_combo = QComboBox()
        self.pair_combo.addItems(config.LIST_PAIR)

        # Интервал
        self.interval_label = QLabel(text.EDITOR_SETTING[self.language][3])
        self.interval_input = QComboBox()
        self.interval_input.addItems(config.LIST_INTERVALS[self.table_agent.exchange])

        # Комиссия
        self.commission_label = QLabel(text.EDITOR_SETTING[self.language][4])
        self.commission_input = QLineEdit()

        # Добавляем значок вопроса рядом с "Комиссия"
        self.commission_help_button = QToolButton()
        self.commission_help_button.setText("?")
        self.commission_help_button.setToolTip("Введите комиссию в формате 0.001 \nКомиссия исмользуестся только для расчетов результатов")  # Текст всплывающей подсказки
        self.commission_help_button.setStyleSheet("""
            QPushButton {
                border: none;
                font-weight: bold;
                color: #007AFF;
                background: transparent;
            }
        """)

        settings_layout.addWidget(self.pair_label)
        settings_layout.addWidget(self.pair_combo)
        settings_layout.addWidget(self.interval_label)
        settings_layout.addWidget(self.interval_input)
        settings_layout.addWidget(self.commission_label)
        settings_layout.addWidget(self.commission_help_button)
        settings_layout.addWidget(self.commission_input)

        QToolTip.setFont(QFont("Arial", 10))
        self.commission_help_button.setToolTipDuration(2000)  # 2000 мс = 2 секунды

        self.layout.addLayout(settings_layout)

        # Редактор кода
        editor_layout = QHBoxLayout()
        # Создаём редактор с подсветкой синтаксиса
        self.editor = AdvancedEditor()
        editor_layout.addWidget(self.editor, stretch=3)

        # **Панель переменных (справа)**
        self.variables_layout = QVBoxLayout()
        self.variables_layout.setAlignment(Qt.AlignTop)  # Выравниваем переменные вверх

        # Кнопка "Добавить переменную"
        self.add_variable_button = QPushButton("➕ Добавить переменную")
        self.add_variable_button.clicked.connect(self.add_variable)
        self.variables_layout.addWidget(self.add_variable_button)

        # Обертка для прокрутки переменных
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_widget = QWidget()
        scroll_area_widget.setLayout(self.variables_layout)
        scroll_area.setWidget(scroll_area_widget)

        # Ограничиваем ширину панели переменных
        scroll_area.setMinimumWidth(200)
        scroll_area.setMaximumWidth(250)
        scroll_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  # Фиксированная ширина

        editor_layout.addWidget(scroll_area)

        # **Общий Layout**
        self.layout.addLayout(editor_layout)  

        # Загружаем настройки и файл
        self.load_all()

    def add_variable(self):
        """Добавляет новую переменную в список переменных"""
        variable_count = len(self.variables_layout) // 3  # Считаем количество добавленных переменных

        # Создаем новый элемент для переменной
        variable_label = QLabel(f"variable_{variable_count + 1}")
        variable_input = QLineEdit()
        variable_input.setValidator(QIntValidator())  # Ограничение ввода только целыми числами

        # Создаем кнопку для удаления переменной
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(lambda: self.delete_variable(variable_label, variable_input, delete_button))

        # Добавляем переменную в панель
        self.variables_layout.addWidget(variable_label)
        self.variables_layout.addWidget(variable_input)
        self.variables_layout.addWidget(delete_button)
       
    def delete_variable(self, label, input_field, delete_button):
        """Удаляет переменную из панели"""
        self.variables_layout.removeWidget(label)
        self.variables_layout.removeWidget(input_field)
        self.variables_layout.removeWidget(delete_button)

        label.deleteLater()
        input_field.deleteLater()
        delete_button.deleteLater()

    def load_all(self):
        """Загружает настройки из БД и код из файла"""
        self.load_settings()
        self.load_file()
        self.load_variables()

    def save_all(self):
        """Сохраняет настройки в БД и код в файл"""
        self.save_settings()
        self.save_file()
        self.save_variables()

    def load_file(self):
        """Загружает файл в редактор"""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.editor.setText(file.read())
            logger.info("Файл загружен в редактор")

    def save_file(self):
        """Сохраняет изменения в файл"""
        with open(self.file_path, "w", encoding="utf-8") as file:
            file.write(self.editor.text())  # Сохраняем текст из редактора в файл
        logger.info("Файл из редактора сохранён!")

    def load_settings(self):
        """Загружает настройки (монетная пара, интервал, комиссия) из БД"""
        try:
            row = self.table_agent.get_data_main_table()
            # print(row)
            if row:
                self.pair_label = QLabel(str(row[0][0]))
                self.pair_combo.setCurrentText(str(row[0][1]))  # Биржа
                self.interval_input.setCurrentText(row[0][2])  # Интервал
                self.commission_input.setText(str(row[0][3]))  # Комиссия
            logger.info("Параметры редактора загружены!")
        except sqlite3.Error as e:
            logger.error(f"Ошибка загрузки параметров редактора: {e}")

    def save_settings(self):
        """Сохраняет настройки (монетная пара, интервал, комиссия) в БД"""
        pair = self.pair_combo.currentText()
        interval = self.interval_input.currentText()
        commission = self.commission_input.text()

        try:
            commission = float(commission)  # Преобразуем в число
        except ValueError:
            logger.error(f"Комиссия должна быть числом!")
            QMessageBox.warning(self, "Ошибка", "Комиссия должна быть числом!")
            return

        commission = float(commission)

        try:
            self.table_agent.record_data_main_table(pair, interval, commission)
            logger.info("Параметры редактора сохранены!")
        except sqlite3.Error as e:
            logger.error(f"Ошибка сохранения параметров редактора: {e}")
    
    def load_variables(self):
        """Загружает переменные из базы данных"""
        # Очищаем текущие переменные
        self.clear_variables()

        try:
            variables = self.table_agent.get_all_variables()  # Получаем все переменные из базы
            for idx, (variable_name, variable_value) in enumerate(variables):
                self.add_variable_from_db(variable_name, variable_value)  # Добавляем переменную в интерфейс
            logger.info("Переменные загружены!")
        except sqlite3.Error as e:
            logger.error(f"Ошибка загрузки переменных: {e}")

    def clear_variables(self):
        """Очищает все переменные в интерфейсе"""
        for i in reversed(range(self.variables_layout.count())):
            widget = self.variables_layout.itemAt(i).widget()
            if widget:
                # Пропускаем кнопку "Добавить переменную" по индексу 0
                if widget != self.add_variable_button:
                    widget.deleteLater()

    def add_variable_from_db(self, variable_name, variable_value):
        """Добавляет переменную из базы данных"""
        variable_label = QLabel(variable_name) # Имя переменной
        variable_input = QLineEdit(str(variable_value)) # Значение переменной

        # Создаем кнопку для удаления переменной
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(lambda: self.delete_variable(variable_label, variable_input, delete_button))

        # Добавляем переменную в панель
        self.variables_layout.addWidget(variable_label)
        self.variables_layout.addWidget(variable_input)
        self.variables_layout.addWidget(delete_button)

    def save_variables(self):
        """Сохраняет все переменные в отдельную таблицу БД"""
        variables = []

        # Собираем все значения переменных
        for i in range(1, self.variables_layout.count(), 3):  # Начинаем с 1, чтобы пропустить кнопку добавления переменной
            variable_label = self.variables_layout.itemAt(i).widget()  # Каждая пара: Label и QLineEdit
            variable_input = self.variables_layout.itemAt(i+1).widget()

            if isinstance(variable_label, QLabel) and isinstance(variable_input, QLineEdit):
                variable_name = variable_label.text()
                variable_value = variable_input.text()
                
                # Добавляем переменную в список
                try:
                    variables.append((variable_name, int(float(variable_value))))
                except:
                    if variable_value.isdigit():  # Проверяем, что значение - число
                        variables.append((variable_name, variable_value))
                    else:
                        QMessageBox.warning(self, "Ошибка", "Переменные должны быть числом!")
                        return

        try:
            self.table_agent.drop_variable_data()
            # Сохраняем каждую переменную в базу данных
            for variable_name, variable_value in variables:
                self.table_agent.record_variable_data(variable_name, variable_value)
            logger.info("Переменные сохранены в таблицу!")
        except sqlite3.Error as e:
            logger.error(f"Ошибка сохранения переменных: {e}")