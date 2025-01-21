import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logging import setup_logging

def main():
    """
        Точка входа
    """
    # Настройка логирования
    setup_logging()

    # Создание экземпляра приложения
    app = QApplication(sys.argv)

    # Инициализация главного окна
    main_window = MainWindow()
    main_window.show()

    # Запуск основного цикла приложения
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()