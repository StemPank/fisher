import logging
import setting as setting
import datetime
from binance.spot import Spot as Client
import pandas as pd
import psycopg2
from psycopg2 import Error

def market_kline():
    with open('./log/logging-market_kline_binance_time.log', 'r') as file:
        for line in file:
            pass
    logging.basicConfig(level=logging.DEBUG, filename='./log/logging-market_kline_binance_time.log', format='(%(asctime)s):', datefmt='%d/%m/%Y %I:%M',
                        encoding = 'utf-8', filemode='w')

    try:
        last_entry_time = datetime.datetime.strptime(line.replace('(', '').replace('):', '').strip(), '%d/%m/%Y %I:%M')
        print(f'Последнее вслючение {last_entry_time}')
        last_entry_time = last_entry_time.timestamp() * 1000
        current_time = datetime.datetime.now().strftime('%d/%m/%Y %I:%M')
        current_time = datetime.datetime.strptime(current_time, '%d/%m/%Y %I:%M').timestamp() * 1000
        insert(last_entry_time, current_time)
    except:
        insert()

def insert(last_entry_time=None, current_time=None):
    spot_client = Client(base_url="https://testnet.binance.vision")
    for name in setting.NAME_SYMBOL:
        if last_entry_time==None and current_time==None:
            data = spot_client.klines(name, "1m")
        else:
            data = spot_client.klines(name, "1m", startTime=int(last_entry_time) , endTime=int(current_time))
        
        all_data = pd.DataFrame(data, columns=["t", "o", "h", "l", "c", "v", "T", "q", "n", "V", "Q", "B"])
        all_data = all_data.drop(index=(len(all_data)-1))
        print(f'Данные получены по символу {name}')

        try:
            connection = psycopg2.connect(user = setting.POSTGRES_USER,
                            password=setting.POSTGRES_PASSWORD,
                            host=setting.POSTGRES_HOST,
                            port=setting.POSTGRES_PORT,
                            database=setting.POSTGRES_DB)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM binance_kline WHERE market = 'folse'")
            connection.commit()
            for i in range(len(all_data)):
                cursor.execute('INSERT INTO binance_kline (name, market, time, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                        (name, 'true', int(all_data.iloc[i, 0]/1000), float(all_data.iloc[i, 1]), float(all_data.iloc[i, 2]), float(all_data.iloc[i, 3]), float(all_data.iloc[i, 4]), float(all_data.iloc[i, 5])))
            connection.commit()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL %s", error)
        finally:
            if connection:
                cursor.close()
                connection.close()

if __name__ == "__main__":
    market_kline()




