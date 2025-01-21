import os, logging

def setup_logging():
    """
        Настаивает систему логирования для приложения
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(ascrime)s - %(levelname)s - %(message)s",
        handlers=[
            #  логи пишшутся в файл 
            logging.FileHandler(os.path.join(os.path.dirname(__file__), "app.log")),
            # логи отображаются в консоли
            logging.StreamHandler()
        ]
    )
    logging.info("Логирование настроено")