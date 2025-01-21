import os, pickle
from PyQt5.QtWidgets import (QFileDialog, QWidget, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHBoxLayout, 
                             QHeaderView, QLineEdit)
import gui.global_variable as global_variable

class SettingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parent = parent  
        
        # Загрузка сохранённых данных
        self.setting_load()

        # Макет
        self.Vlayout = QVBoxLayout()
        self.Vlayout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        self.layout_path = QHBoxLayout()
        self.Vlayout.addLayout(self.layout_path)
        
            # Текстовое поле
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Выберите папку...")
        self.folder_path.setPlaceholderText(self.folder_path_text)
        self.layout_path.addWidget(self.folder_path)

            # Кнопка
        self.browse_button = QPushButton("...")
        self.browse_button.setFixedWidth(30)  # Фиксированная ширина кнопки
        self.browse_button.clicked.connect(self.select_folder)
        self.layout_path.addWidget(self.browse_button)
        
        self.layout_button = QHBoxLayout()
        self.Vlayout.addLayout(self.layout_button)
        add_agent_button = QPushButton("Сохранить")
        add_agent_button.clicked.connect(self.setting_save)
        self.layout_button.addStretch()
        self.layout_button.addWidget(add_agent_button)

        self.setLayout(self.Vlayout)

    def select_folder(self):
        """Открывает диалоговое окно для выбора папки."""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:  # Если пользователь выбрал папку
            self.folder_path.setText(folder)
    
    def setting_save(self):
        """Созраняет настройки"""
        # os.path.join(os.path.join(os.path.dirname(__file__), "main"), "setting.pkl")
        state = {
            "folder_path": self.folder_path.text(),
        }
        with open(global_variable.SETTING_FILE, "wb") as file:
            pickle.dump(state, file)

    def setting_load(self):
        """Загрузка видимости выбранных настроек"""
        if os.path.exists(global_variable.SETTING_FILE):
            with open(global_variable.SETTING_FILE, "rb") as file:
                state = pickle.load(file)
                if state.get("folder_path"):
                    self.folder_path_text = state.get("folder_path")