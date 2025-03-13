import os, pickle, datetime
import re
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLineEdit, QLabel, QDialogButtonBox, 
                             QDateEdit, QCheckBox, QMessageBox
                             )
from PyQt5.QtCore import QDate

import paths, global_variable, gui.texts as texts, config

from utils.logging import logger

def validate_input(method):
    """Декоратор для проверки имени агента перед закрытием диалогового окна."""
    def wrapper(self):
        name = self.name_input.text().strip()

        # Проверка: имя должно содержать только буквы, цифры и _
        if not re.match(r"^[a-zA-Z0-9_]{3,10}$", name):
            self.error_label.setText("Имя должно содержать 3-10 символов (буквы, цифры, _).")
            self.error_label.show()
            return  # Не закрываем диалоговое окно
        
        self.error_label.hide()  # Если ошибок нет, скрываем ошибку
        return method(self)  # Вызываем оригинальный метод `accept`
    
    return wrapper

class AgentDialog(QDialog):
    def __init__(self, parent=None, language=None):
        super().__init__(parent)  # Теперь parent передается в QDialog
        self.language = language
        self.exchanges = global_variable.registered_data_providers()
        
        self.setWindowTitle(texts.DIALOG_AGENTS_ADD[self.language])
        self.setFixedSize(350, 180)

        layout = QVBoxLayout()

        # Поле ввода имени агента
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(texts.DIALOG_AGENTS_ADD_FORM[self.language][1])
        layout.addWidget(QLabel(texts.DIALOG_AGENTS_ADD_FORM[self.language][0]))
        layout.addWidget(self.name_input)

        # Метка для отображения ошибки (изначально скрыта)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.hide()
        layout.addWidget(self.error_label)

        # Выпадающий список бирж
        self.exchange_select = QComboBox()
        self.exchange_select.addItems(self.exchanges)
        layout.addWidget(QLabel(texts.DIALOG_AGENTS_ADD_FORM[self.language][2]))
        layout.addWidget(self.exchange_select)

        # Кнопки OK / Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept) # Используем декорированный accept
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    @validate_input
    def accept(self):
        """Закрывает диалоговое окно только при корректном вводе."""
        super().accept()

    def get_data(self):
        """Возвращает имя агента и выбранную биржу."""
        return self.name_input.text(), self.exchange_select.currentText()


class SettingsDialog(QDialog):
    def __init__(self, parent=None, agent_name=None, language=None):
        super().__init__(parent)

        self.agent_name = agent_name
        self.language = language
        self.exchanges = global_variable.registered_data_providers()
        
        self.exchange_options = config.LIST_OF_AVAILABLE_BASE_ENDPOINTS
        self.agent_path = global_variable.setting_file("folder_path")

        self.setWindowTitle(f"{texts.DIALOG_AGENTS_SETTING[self.language]}: {agent_name}")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        
        # Выпадающий список бирж
        self.exchange_select = QComboBox()
        self.exchange_select.addItems(self.exchanges)
        self.exchange_select.currentTextChanged.connect(self.update_sub_options)
        layout.addWidget(QLabel(texts.DIALOG_AGENTS_ADD_FORM[self.language][2]))
        layout.addWidget(self.exchange_select)

        # Второй выпадающий список, зависит от первого
        self.sub_option_select = QComboBox()
        layout.addWidget(QLabel("Дополнительный параметр:"))
        layout.addWidget(self.sub_option_select)

        # Поля выбора даты
        layout.addWidget(QLabel("Дата начала:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)  # Всплывающий календарь
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.start_date_edit)
        
        # Поля выбора даты
        layout.addWidget(QLabel("Дата конца:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.end_date_edit)

        # Галочка "До текущей даты"
        self.current_date_checkbox = QCheckBox("До текущей даты")
        self.current_date_checkbox.stateChanged.connect(self.toggle_end_date)
        layout.addWidget(self.current_date_checkbox)

        # Кнопки управления
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

        # Загрузка сохранённых данных
        self.load_settings()
    
    def update_sub_options(self):
        """Обновляет второй список в зависимости от выбранного значения первого."""
        # selected_exchange = self.exchange_select.currentText()
        selected_exchange = global_variable.registered_data_providers(self.exchange_select.currentText(), exc=True)
        self.sub_option_select.clear()
        if selected_exchange in self.exchange_options:
            self.sub_option_select.addItems(self.exchange_options[selected_exchange])

    def toggle_end_date(self, state):
        """Отключает выбор конечной даты, если галочка активна."""
        if state == 2:  # Checked
            self.end_date_edit.setDisabled(True)
            self.end_date_edit.setDate(QDate.currentDate())
        else:  # Unchecked
            self.end_date_edit.setDisabled(False)

    def save_settings(self):
        """Сохраняет выбранные даты и состояние галочки в файл."""
        settings = {
            "exchange": self.exchange_select.currentText(),
            "sub_option": self.sub_option_select.currentText(),
            "start_date": self.start_date_edit.date().toPyDate(),
            "end_date": self.end_date_edit.date().toPyDate(),
            "current_date_enabled": self.current_date_checkbox.isChecked(),
        }

        
        filename = f"{self.agent_path}/{self.agent_name}/{self.agent_name}_settings.pkl"

        with open(filename, "wb") as file:
            pickle.dump(settings, file)

        self.accept()

    def load_settings(self):
        """Загружает сохранённые даты и состояние галочки из файла, если файл существует."""
        filename = f"{self.agent_path}/{self.agent_name}/{self.agent_name}_settings.pkl"

        if os.path.exists(filename):
            with open(filename, "rb") as file:
                settings = pickle.load(file)

            # Выбираем биржу в выпадающем списке
            exchange = settings.get("exchange")
            if exchange and exchange in self.exchanges:
                self.exchange_select.setCurrentText(exchange)

            try:
                selected_exchange = global_variable.registered_data_providers(exchange, exc=True)
                sub_option = settings.get("sub_option")
                logger.debug(f"Загрузка сохраненных настроек агента {self.agent_name}: Имя поставщика {exchange}, Поставщик {selected_exchange}, Конечная тачка {sub_option}")
                if sub_option and sub_option in self.exchange_options.get(selected_exchange, []):
                    self.sub_option_select.setCurrentText(sub_option)
            except Exception as e:
                logger.warning(f"Ошибка, нет данных о поставщике: {e}")
                QMessageBox.information(self, "Ошибка", "Нет данных о поставщике")

            # Установка сохранённых значений
            start_date_value = settings.get("start_date")
            end_date_value = settings.get("end_date")
            current_date_enabled = settings.get("current_date_enabled", False)

            # Преобразование в QDate
            if isinstance(start_date_value, (str, datetime.date)):
                start_date = (
                    QDate.fromString(start_date_value, "yyyy-MM-dd")
                    if isinstance(start_date_value, str)
                    else QDate(start_date_value.year, start_date_value.month, start_date_value.day)
                )
                if start_date.isValid():
                    self.start_date_edit.setDate(start_date)

            if isinstance(end_date_value, (str, datetime.date)):
                end_date = (
                    QDate.fromString(end_date_value, "yyyy-MM-dd")
                    if isinstance(end_date_value, str)
                    else QDate(end_date_value.year, end_date_value.month, end_date_value.day)
                )
                if end_date.isValid():
                    self.end_date_edit.setDate(end_date)

            # Установка состояния галочки
            self.current_date_checkbox.setChecked(current_date_enabled)
            self.toggle_end_date(2 if current_date_enabled else 0)  # Применить состояние галочки