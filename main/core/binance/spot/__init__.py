"""
    Наличие файла __init__.py в директории говорит Python, что эта директория является пакетом.
    Например, если у вас есть структура:
        my_project/
        ├── core/
        │   ├── __init__.py
        │   ├── strategies.py
        │   └── api_handler.py
    Теперь вы можете импортировать модули из папки core:
        from core.strategies import some_function
    Инициализация пакета

    В __init__.py можно разместить код, который выполнится при первом импорте пакета.
    Например, вы можете импортировать модули пакета для упрощения доступа:
        # core/__init__.py
        from .strategies import run_strategy
        from .api_handler import connect_to_api
    Теперь можно импортировать функции напрямую из пакета:
        from core import run_strategy, connect_to_api
    Контроль над экспортируемыми объектами

    С помощью переменной __all__ можно указать, какие модули или функции будут доступны при использовании импорта с *:
        # core/__init__.py
        __all__ = ['run_strategy', 'connect_to_api']
    Организация структуры большого проекта

    В проектах с большой кодовой базой __init__.py помогает сделать пакеты понятными и удобными для навигации.
    """


# MARKETS
from ._market import klines