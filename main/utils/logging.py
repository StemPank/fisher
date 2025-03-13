import logging, os, datetime
import paths

def clean_old_logs(days=30):
    """Удаляет строки из лог-файла, которые старше указанного количества дней."""
    if not os.path.exists(paths.LOG_FILE):
        logger.info(f"Файл {paths.LOG_FILE} не найден.")
        return

    # Читаем лог
    with open(paths.LOG_FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Получаем текущую дату
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    new_lines = []

    for line in lines:
        try:
            # Извлекаем дату из строки лога (формат должен соответствовать логам)
            log_date_str = line.split(" ")[0]  # Берем первую часть (дата)
            log_date = datetime.datetime.strptime(log_date_str, "%Y-%m-%d")  # Подстрой под свой формат

            # Оставляем только свежие записи
            if log_date >= cutoff_date:
                new_lines.append(line)
        except (ValueError, IndexError):
            # Если строка не содержит дату в ожидаемом формате, оставляем её
            new_lines.append(line)

    # Перезаписываем файл без старых записей
    with open(paths.LOG_FILE, "w", encoding="utf-8") as file:
        file.writelines(new_lines)

    logger.info(f"Очищены старые логи.")

# Создаем логгер
logger = logging.getLogger("APP")
logger.setLevel(logging.DEBUG)  # Логгер пишет всё, но обработчики фильтруют

# Создаем логгер
logger_agent = logging.getLogger("AGENT")
logger_agent.setLevel(logging.DEBUG)  # Логгер пишет всё, но обработчики фильтруют

# --- 1. Лог в файл (всё, включая DEBUG) ---
file_handler = logging.FileHandler(paths.LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # Записывает все уровни логов
file_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
)
file_handler.setFormatter(file_formatter)

# --- 2. Лог в консоль (без DEBUG) ---
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Выводит только INFO и выше
console_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
console_handler.setFormatter(console_formatter)

# Добавляем обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Добавляем обработчики в логгер
logger_agent.addHandler(file_handler)
logger_agent.addHandler(console_handler)