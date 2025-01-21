import os, pickle, datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QLabel, QDialogButtonBox, 
                             QDateEdit, QCheckBox
                             )
from PyQt5.QtCore import QDate
import gui.global_variable as global_variable

class AgentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить агента")
        self.setFixedSize(300, 100)

        layout = QVBoxLayout()

        # Поле ввода текста
        self.name_input = QLineEdit() # Выджет редактируемой строки
        self.name_input.setPlaceholderText("Имя агента")
        # layout.addWidget(QLabel("Введите имя агента:"))
        layout.addWidget(self.name_input) # Добавить на макет

        # Кнопки диалогового окна
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_name(self):
        return self.name_input.text()

class SettingsDialog(QDialog):
    def __init__(self, agent_name=None, parent=None):
        super().__init__(parent)

        self.agent_name = agent_name
        setting = global_variable.setting_file()
        if setting.get("folder_path"):
            self.agent_path = setting.get("folder_path")
        # self.agent_path = global_variable.setting_file()

        self.setWindowTitle(f"Настройки агента: {agent_name}")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Настройки для агента: {agent_name}"))

        # Поля выбора даты
        date_layout = QHBoxLayout()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)  # Всплывающий календарь
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(QLabel("Дата начала:"))
        date_layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(QLabel("Дата конца:"))
        date_layout.addWidget(self.end_date_edit)

        layout.addLayout(date_layout)

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
            "start_date": self.start_date_edit.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date_edit.date().toString("yyyy-MM-dd"),
            "current_date_enabled": self.current_date_checkbox.isChecked(),
        }

        # Уникальный файл для каждого агента
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