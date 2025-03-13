from setuptools import setup, find_packages

setup(
    name="my_agents",  # Название пакета
    version="1.0",
    packages=find_packages(),  # Автоматически находит модули
    py_modules=["bind_agents", "agent_indicators"],  # Добавляем модули без подпапок
    install_requires=[]  # Можно указать зависимости, если есть
)