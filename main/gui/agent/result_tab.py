import os
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import global_variable  # Убедитесь, что этот модуль доступен
from utils.logging import logger

class ResultsTab(QWidget):
    def __init__(self, agent_name):
        super().__init__()
        self.agent_name = agent_name
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Кнопка обновления
        self.update_button = QPushButton("Обновить данные")
        self.update_button.clicked.connect(self.load_data)
        layout.addWidget(self.update_button)

        # Таблица для отображения данных
        self.table = QTableWidget()
        self.table.setColumnCount(17)  # Укажите количество колонок
        self.table.setHorizontalHeaderLabels([
            "Количество сделок", "Прибыльных сделок", "Убыточных сделок", "Общая прибыль", "Общий убыток", "Чистая прибыль",
            "Средняя прибыль на сделку", "Процент прибыльных сделок", "Фактор прибыли", "Ожидаемая доходность сделки", "Максимальная просадка",
            "Коэффициент восстановления", "Коэффициент Шарпа", "Коэффициент Калмара", "ROI - Доходность на капитал", "ROE - с учетом плеча", "Стандартное отклонение доходности", "Средняя длительность сделки"
        ])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        """Загружает все строки из БД и отображает первые 17 значений."""
        db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), self.agent_name), f'agent_data_{self.agent_name}.sqlite')

        if not os.path.exists(db_path):
            logger.warning("База данных не найдена.")
            QMessageBox.warning(self, "Ошибка", "База данных не найдена.")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM results")
            rows = cursor.fetchall()

            if not rows:
                logger.info("Нет данных для отображения.")
                QMessageBox.information(self, "Данные", "Нет данных для отображения.")
                return

            # Очищаем таблицу перед обновлением
            self.table.setRowCount(0)

            # Функция округления значений
            def format_value(value):
                if isinstance(value, (float, int)):
                    return f"{value:.3f}"
                return str(value)

            # Заполняем таблицу
            for row in rows:
                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)

                for col_idx in range(19):  # Берем только первые 17 значений
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(format_value(row[col_idx + 1])))

            conn.close()
        except Exception as e:
            logger.critical(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")