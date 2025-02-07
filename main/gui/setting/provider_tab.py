import sys, os
from dotenv import load_dotenv, set_key, unset_key

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QDialog, QLabel, QLineEdit, QComboBox, QFormLayout, QHBoxLayout, QHeaderView
)
from PyQt5.QtGui import QIcon, QBrush
from PyQt5.QtCore import QSettings, QSize

import paths, config, global_variable, gui.texts as texts

# Загружаем переменные окружения из .env
ENV_FILE = os.path.join(paths.CONFIG_PATH, ".env")
load_dotenv(ENV_FILE)
"""
    os.path.join(paths.CONFIG_PATH, ".env") — формирует полный путь к .env файлу.
    load_dotenv(ENV_FILE) — загружает переменные окружения из .env в os.environ, после чего их можно получить через os.getenv("ПЕРЕМЕННАЯ").
"""


class ProviderTab(QWidget):
    def __init__(self, parent=None, language=None):
        super().__init__(parent)
        self.parent = parent  
        self.language = language

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(texts.PROVIDER_TABLE_HEADERS[self.language])
        self.table.horizontalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setColumnWidth(2, 40)
        self.table.horizontalHeader().setStretchLastSection(False) # Запрет изменения размеров колонок
        self.table.setEditTriggers(QTableWidget.NoEditTriggers) # Запрет редактирования таблицы
        self.layout.addWidget(self.table)

        add_button = QPushButton()
        add_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-plus.png")))
        add_button.setIconSize(QSize(24, 24))
        add_button.clicked.connect(self.add_provider)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(add_button)

        self.layout.addLayout(button_layout)

        self.load_providers()

    def load_providers(self):
        """Загружает данные из .env в таблицу"""
        for key, value in os.environ.items():
            if key.startswith("PROVIDER_"):
                name, exchange, _, _ = value.split("|")
                self.add_to_table(name, exchange)

    def add_provider(self):
        """Добавляет нового поставщика"""
        dialog = AddProviderDialog(self, self.language)
        if dialog.exec_():
            name, exchange, api_key, secret_key = dialog.get_data()
            self.add_to_table(name, exchange)
            self.save_provider(name, exchange, api_key, secret_key)

    def add_to_table(self, name, exchange):
        """Добавляет поставщика в таблицу"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(exchange))

        delete_button = QPushButton()
        delete_button.setIcon(QIcon(os.path.join(paths.ICONS_PATH, "icon-trash.png")))
        delete_button.clicked.connect(lambda: self.remove_provider(name, row))
        self.table.setCellWidget(row, 2, delete_button)

    def save_provider(self, name, exchange, api_key, secret_key):
        """Сохраняет поставщика в .env"""
        set_key(ENV_FILE, f"PROVIDER_{name}", f"{name}|{exchange}|{api_key}|{secret_key}")

    def remove_provider(self, name, row):
        """Удаляет поставщика из .env и таблицы"""
        unset_key(ENV_FILE, f"PROVIDER_{name}")
        self.table.removeRow(row)

class AddProviderDialog(QDialog):
    def __init__(self, parent=None, language=None):
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(texts.DIALOG_PROVIDERS_ADD[self.language])
        self.setFixedSize(300, 200)


        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.exchange_input = QComboBox()
        self.exchange_input.addItems(config.LIST_PROVIDERS)
        self.api_key_input = QLineEdit()
        self.secret_key_input = QLineEdit()

        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][0], self.name_input)
        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][1], self.exchange_input)
        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][2], self.api_key_input)
        form_layout.addRow(texts.DIALOG_PROVIDERS_ADD_FORM[self.language][3], self.secret_key_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(texts.DIALOG_BUTTON[self.language][0])
        self.cancel_button = QPushButton(texts.DIALOG_BUTTON[self.language][1])

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        return (
            self.name_input.text(),
            self.exchange_input.currentText(),
            self.api_key_input.text(),
            self.secret_key_input.text(),
        )
