import logging
import setting as setting
import datetime
from binance.spot import Spot as Client
import pandas as pd
import psycopg2
from psycopg2 import Error

def market_kline():
    try:
        with open('./main/log/logging-market_kline_binance_time.log', 'r') as file:
            for line in file:
                pass
        last_entry_time = datetime.datetime.strptime(line.replace('(', '').replace('):', '').strip(), '%d/%m/%Y %I:%M')
        print(f'Последнее вслючение {last_entry_time}')
    except:
        pass
    logging.basicConfig(level=logging.DEBUG, filename='./main/log/logging-market_kline_binance_time.log', format='(%(asctime)s):', datefmt='%d/%m/%Y %I:%M',
                        encoding = 'utf-8', filemode='w')
    

    spot_client = Client(base_url="https://testnet.binance.vision")
    for name in setting.NAME_SYMBOL:
        try:
            connection = psycopg2.connect(user = setting.POSTGRES_USER,
                                password=setting.POSTGRES_PASSWORD,
                                host=setting.POSTGRES_HOST,
                                port=setting.POSTGRES_PORT,
                                database=setting.POSTGRES_DB)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM binance_kline WHERE market = 'folse'")
            connection.commit()   
            cursor.execute("SELECT * FROM binance_kline WHERE name = '" + name + "'" )
            get_all = pd.DataFrame(cursor.fetchall(), columns=['index', 'name', 'market', 'time', 'open', 'high', 'low', 'close', 'volume'])
            get_all = get_all.drop(['index'], axis= "columns")
            try:
                start_time_req = datetime.datetime.strptime(setting.START_TIME, '%d/%m/%Y').timestamp()
                try:   
                    start_time_fact = get_all['time'].iloc [0]
                    result = start_time_req - start_time_fact
                    if (result * -1 if result <= 0 else result) >90000:
                        cursor.execute("DELETE FROM binance_kline WHERE name = '" + name + "'")
                        connection.commit()
                        start_time_req = start_time_req*1000
                    else:
                        start_time_req = None
                except:
                    start_time_req = start_time_req*1000
            except:
                start_time_req = None
            
            try:
                last_entry_time = get_all['time'].iloc [-1]*1000
            except:
                last_entry_time = None
            
            current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
            # print(f'Дата теста: {current_time}')
            current_time_timestamp  = datetime.datetime.strptime(current_time, '%d/%m/%Y %H:%M').timestamp() * 1000
            # print(f'Дата теста: {current_time_timestamp }')
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL %s", error)
            print("Невозможно загрузить исторически данные")
            break
        finally:
            if connection:
                cursor.close()
                connection.close()

        if start_time_req==None and last_entry_time==None:
            # print('defolt')
            data = spot_client.klines(name, "1m")
        if start_time_req==None and last_entry_time!=None:
            # print(f'last_entry_time = {last_entry_time}')
            data = spot_client.klines(name, "1m", startTime=int(last_entry_time), endTime=int(current_time_timestamp))
        if start_time_req!=None:
            # print(f'start_time_req = {start_time_req}')
            # print(f'current_time_timestamp = {current_time_timestamp}')
            data = spot_client.klines(name, "1m", startTime=int(start_time_req), endTime=int(current_time_timestamp))
        try:
            all_data = pd.DataFrame(data, columns=["t", "o", "h", "l", "c", "v", "T", "q", "n", "V", "Q", "B"])
            all_data = all_data.drop(index=(len(all_data)-1))
            all_data = all_data.drop(index=(0))
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


                # cursor.execute("SELECT * FROM binance_kline WHERE name = '" + name + "'" )
                # get_all = pd.DataFrame(cursor.fetchall(), columns=['index', 'name', 'market', 'time', 'open', 'high', 'low', 'close', 'volume'])
                # get_all = get_all.drop(['index'], axis= "columns")
                # print(get_all)


            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL %s", error)
                print("Невозможно загрузить исторически данные")
            finally:
                if connection:
                    cursor.close()
                    connection.close()
        except:
            pass

if __name__ == "__main__":
    market_kline()




