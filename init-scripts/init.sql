CREATE TABLE binance_kline (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    market VARCHAR(50) NOT NULL,
    time INT NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL
);

CREATE TABLE bybit_kline (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    market VARCHAR(50) NOT NULL,
    time INT NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL
);