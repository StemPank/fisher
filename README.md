
Заготовка под написани торгового бота

Для запуска:
    
Установить библиотеки:
    pip install -r requirements.txt 

Создать файлы из .gitignore:
    main\setting.py
        NAME_SYMBOL = ['BTCUSDT', 'ETHUSDT'] - писать свои, от 1 до сколько хотите

        POSTGRES_HOST = 'localhost'
        POSTGRES_USER = 'user'
        POSTGRES_DB = 'database'
        POSTGRES_PASSWORD = 'password'
        POSTGRES_PORT = '5433'

Docker для запуска контейнера БД (Пока не нужен)
Пример docker-compose.yml:
    version: "3.9"
    services:
        postgres:
            container_name: "my_db"
            restart: always
            image: postgres:16.3
            environment:
            POSTGRES_DB: "database"
            POSTGRES_USER: "user"
            POSTGRES_PASSWORD: "password"
            volumes:
            - .\pgdata:/var/lib/postgresql/data
            - .\init-scripts:/docker-entrypoint-initdb.d
            ports:
            - "5433:5432"
Docker команды:
    docker-compose -f docker-compose.yml up --force-recreate - запустить контейнер и создать таблицы БД
    docker-compose dawn -v - остановить и удалить контейнер
    docker ps - для проверки

Расширения
cweijan.vscode-mysql-client2 - для подключение к БД

Полезная информация:

Binance

Git - https://github.com/binance/binance-connector-python
API documentation - https://binance-docs.github.io/apidocs/spot/en/#websocket-market-streams
Форум разработчиков - https://dev.binance.vision/search?q=Quote%20asset%20volume

The following base endpoints are available:
    https://api.binance.com
    https://api-gcp.binance.com
    https://api1.binance.com
    https://api2.binance.com
    https://api3.binance.com
    https://api4.binance.com



Bybit

Git - https://github.com/bybit-exchange/pybit
API documentation - https://bybit-exchange.github.io/docs/v5/intro

Address Segment	Description
    v5/market/	Candlestick, orderbook, ticker, platform transaction data, underlying financial rules, risk control rules
    v5/order/	Order management
    v5/position/	Position management
    v5/account/	Single account operations only – unified funding account, rates, etc.
    v5/asset/	Operations across multiple accounts – asset management, fund management, etc.
    v5/spot-lever-token/	Obtain quotes from Leveraged Tokens on Spot, and to exercise purchase and redeem functions
    v5/spot-margin-trade/	Manage Margin Trading on Spot