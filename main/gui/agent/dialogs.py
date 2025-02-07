import os, pickle, datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QComboBox,
                             QLineEdit, QLabel, QDialogButtonBox, 
                             QDateEdit, QCheckBox
                             )
from PyQt5.QtCore import QDate

import paths, global_variable, gui.texts as texts

class AgentDialog(QDialog):
    def __init__(self, parent=None, language=None):
        super().__init__(parent)  # Теперь parent передается в QDialog
        self.language = language
        self.exchanges = global_variable.registered_data_providers()
        
        self.setWindowTitle(texts.DIALOG_AGENTS_ADD[self.language])
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        # Поле ввода имени агента
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(texts.DIALOG_AGENTS_ADD_FORM[self.language][1])
        layout.addWidget(QLabel(texts.DIALOG_AGENTS_ADD_FORM[self.language][0]))
        layout.addWidget(self.name_input)

        # Выпадающий список бирж
        self.exchange_select = QComboBox()
        self.exchange_select.addItems(self.exchanges)
        layout.addWidget(QLabel(texts.DIALOG_AGENTS_ADD_FORM[self.language][2]))
        layout.addWidget(self.exchange_select)

        # Кнопки OK / Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_data(self):
        """Возвращает имя агента и выбранную биржу."""
        return self.name_input.text(), self.exchange_select.currentText()


class SettingsDialog(QDialog):
    def __init__(self, parent=None, agent_name=None, language=None):
        super().__init__(parent)

        self.agent_name = agent_name
        self.language = language
        self.exchanges = global_variable.registered_data_providers()
        self.agent_path = global_variable.AGENTS_FOLDER

        self.setWindowTitle(f"{texts.DIALOG_AGENTS_SETTING[self.language]}: {agent_name}")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        
        # Выпадающий список бирж
        self.exchange_select = QComboBox()
        self.exchange_select.addItems(self.exchanges)
        layout.addWidget(QLabel(texts.DIALOG_AGENTS_ADD_FORM[self.language][2]))
        layout.addWidget(self.exchange_select)

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