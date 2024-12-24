import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenu, QMenuBar, QAction, QTabWidget, QWidget,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QDialog, QLabel, QDialogButtonBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class AgentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить агента")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя агента")
        layout.addWidget(QLabel("Введите имя агента:"))
        layout.addWidget(self.name_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_name(self):
        return self.name_input.text()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Программа на PyQt5")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        # Меню бар
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        # Меню "Инструменты"
        tools_menu = QMenu("Инструменты", self)
        menu_bar.addMenu(tools_menu)

        self.agent_action = QAction("Агент", self, checkable=True)
        self.agent_action.toggled.connect(self.toggle_agent_tab)
        tools_menu.addAction(self.agent_action)

        self.test_action = QAction("Тест", self, checkable=True)
        tools_menu.addAction(self.test_action)

        # Меню "Действия"
        actions_menu = QMenu("Действия", self)
        menu_bar.addMenu(actions_menu)

        action1 = QAction("Действие 1", self)
        actions_menu.addAction(action1)

        action2 = QAction("Действие 2", self)
        actions_menu.addAction(action2)

        # Центральный виджет
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

    def toggle_agent_tab(self, checked):
        if checked:
            self.add_agent_tab()
        else:
            self.remove_agent_tab()

    def add_agent_tab(self):
        if not hasattr(self, "agent_tab"):
            self.agent_tab = QWidget()
            layout = QVBoxLayout()

            # Таблица
            self.agent_table = QTableWidget()
            self.agent_table.setColumnCount(5)
            self.agent_table.setHorizontalHeaderLabels([
                "Имя агента", "Старт", "Стоп", "Настройки", "Удалить"
            ])
            self.agent_table.horizontalHeader().setStretchLastSection(True)
            layout.addWidget(self.agent_table)

            # Кнопка добавления агента
            add_agent_button = QPushButton("+")
            add_agent_button.clicked.connect(self.add_agent)
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            button_layout.addWidget(add_agent_button)
            layout.addLayout(button_layout)

            self.agent_tab.setLayout(layout)
            self.tabs.addTab(self.agent_tab, "Агент")

    def remove_agent_tab(self):
        index = self.tabs.indexOf(self.agent_tab)
        if index != -1:
            self.tabs.removeTab(index)
            del self.agent_tab

    def add_agent(self):
        dialog = AgentDialog(self)
        if dialog.exec() == QDialog.Accepted:
            agent_name = dialog.get_name()
            if agent_name:
                row_position = self.agent_table.rowCount()
                self.agent_table.insertRow(row_position)

                # Имя агента
                self.agent_table.setItem(row_position, 0, QTableWidgetItem(agent_name))

                # Кнопка "Старт"
                start_button = QPushButton()
                start_button.setIcon(QIcon.fromTheme("media-playback-start"))
                start_button.clicked.connect(lambda: self.start_agent(agent_name))
                self.agent_table.setCellWidget(row_position, 1, start_button)

                # Кнопка "Стоп"
                stop_button = QPushButton()
                stop_button.setIcon(QIcon.fromTheme("media-playback-stop"))
                stop_button.clicked.connect(lambda: self.stop_agent(agent_name))
                self.agent_table.setCellWidget(row_position, 2, stop_button)

                # Кнопка "Настройки"
                settings_button = QPushButton()
                settings_button.setIcon(QIcon.fromTheme("preferences-system"))
                settings_button.clicked.connect(lambda: self.configure_agent(agent_name))
                self.agent_table.setCellWidget(row_position, 3, settings_button)

                # Кнопка "Удалить"
                delete_button = QPushButton()
                delete_button.setIcon(QIcon.fromTheme("edit-delete"))
                delete_button.clicked.connect(lambda: self.delete_agent(row_position))
                self.agent_table.setCellWidget(row_position, 4, delete_button)

    def start_agent(self, name):
        print(f"Запуск агента: {name}")

    def stop_agent(self, name):
        print(f"Остановка агента: {name}")

    def configure_agent(self, name):
        print(f"Настройки агента: {name}")

    def delete_agent(self, row):
        self.agent_table.removeRow(row)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())