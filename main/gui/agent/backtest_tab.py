import os
import sqlite3
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import global_variable  # Убедитесь, что этот модуль доступен
from utils.logging import logger

class BacktestEditor(QWidget):
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

        # Таблица с результатами
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Три колонки: Все сделки, Покупка, Продажа
        self.table.setRowCount(17)  # Количество строк (метрики)
        self.table.setHorizontalHeaderLabels(["Все сделки", "Покупка", "Продажа"])
        self.table.setVerticalHeaderLabels([
            "Количество сделок", 
            "Прибыльных сделок", 
            "Убыточных сделок", "Общая прибыль", "Общий убыток", "Чистая прибыль",
            "Средняя прибыль на сделку", 
            "Процент прибыльных сделок", 
            "Фактор прибыли (Значение > 1 показывает, что стратегия прибыльная.)", 
            "Ожидаемая доходность сделки (Если Expectancy > 0, значит стратегия прибыльная на длинной дистанции.)", 
            "Максимальная просадка (Выражается в % и показывает, насколько опасна стратегия)",
            "Коэффициент восстановления (Чем выше, тем быстрее стратегия восстанавливает убытки.)", 
            "Коэффициент Шарпа (Чем выше, тем лучше)", 
            "Коэффициент Калмара (Помогает оценить, насколько стратегия устойчива к рискам.)", 
            "ROI (Доходность на капитал)", 
            "ROE (Доходность с учетом плеча)", 
            "Стандартное отклонение доходности (Показывает волатильность доходов)"
        ])
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_data(self):
        """Загружает данные из БД и обновляет таблицу."""
        db_path = os.path.join(os.path.join(global_variable.setting_file("folder_path"), self.agent_name), f'agent_data_{self.agent_name}.sqlite')

        if not os.path.exists(db_path):
            logger.warning("База данных не найдена.")
            QMessageBox.warning(self, "Ошибка", "База данных не найдена.")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM results WHERE ideniteration = 1")
            row = cursor.fetchone()

            if not row:
                logger.info("Нет данных для отображения.")
                QMessageBox.information(self, "Данные", "Нет данных для отображения.")
                return

            # Индексы данных в таблице results
            indices = {
                "total_transactions": 1, "profitable_trades": 2, "unprofitable_trades": 3,
                "total_profit": 4, "total_loss": 5, "net_profit": 6, "avg_profit_per_trade": 7,
                "win_rate": 8, "profit_factor": 9, "expectancy": 10, "max_drawdown": 11,
                "recovery_factor": 12, "sharpe_ratio": 13, "calmar_ratio": 14, "roi": 15, "roe": 16,
                "avg_trade_duration": 17,

                "buy_total_transactions": 19, "buy_profitable_trades": 20, "buy_unprofitable_trades": 21,
                "buy_total_profit": 22, "buy_total_loss": 23, "buy_net_profit": 24, "buy_avg_profit_per_trade": 25,
                "buy_win_rate": 26, "buy_profit_factor": 27, "buy_expectancy": 28, "buy_max_drawdown": 29,
                "buy_recovery_factor": 30, "buy_sharpe_ratio": 31, "buy_calmar_ratio": 32, "buy_roi": 33, "buy_roe": 34,
                "buy_avg_trade_duration": 35,

                "sell_total_transactions": 37, "sell_profitable_trades": 38, "sell_unprofitable_trades": 39,
                "sell_total_profit": 40, "sell_total_loss": 41, "sell_net_profit": 42, "sell_avg_profit_per_trade": 43,
                "sell_win_rate": 44, "sell_profit_factor": 45, "sell_expectancy": 46, "sell_max_drawdown": 47,
                "sell_recovery_factor": 48, "sell_sharpe_ratio": 49, "sell_calmar_ratio": 50, "sell_roi": 51, "sell_roe": 52,
                "sell_avg_trade_duration": 53
            }

            # Функция округления значений
            def format_value(value):
                if isinstance(value, (float, int)):
                    return f"{value:.3f}"
                return str(value)

            # Заполняем таблицу
            for row_idx, key in enumerate([
                "total_transactions", "profitable_trades", "unprofitable_trades",
                "total_profit", "total_loss", "net_profit", "avg_profit_per_trade",
                "win_rate", "profit_factor", "expectancy", "max_drawdown",
                "recovery_factor", "sharpe_ratio", "calmar_ratio", "roi", "roe",
                "avg_trade_duration"
            ]):
                self.table.setItem(row_idx, 0, QTableWidgetItem(format_value(row[indices[key]])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(format_value(row[indices["buy_" + key]])))
                self.table.setItem(row_idx, 2, QTableWidgetItem(format_value(row[indices["sell_" + key]])))

            conn.close()
        except Exception as e:
            logger.critical(f"Ошибка загрузки данных: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {e}")