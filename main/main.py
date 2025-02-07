import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.agent.defot_file import create_defolt_file_setting

def main():
    """
        Точка входа
    """
    # создание дефолтного файла настроек приложения
    create_defolt_file_setting() 

    # Создание экземпляра приложения
    app = QApplication(sys.argv)

    # Инициализация главного окна
    main_window = MainWindow()
    main_window.show()

    # Запуск основного цикла приложения
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
