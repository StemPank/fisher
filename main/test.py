import psycopg2
from psycopg2 import Error
import setting
import datetime

time = datetime.datetime.now().strftime('%d/%m/%Y  %I:%M')
print(f'Дата теста: {time}')
timestamp_ms = datetime.datetime.strptime(time, '%d/%m/%Y %I:%M').timestamp() * 1000
print(f'Дата теста: {timestamp_ms}')
timestamp = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
print(f'Дата теста: {timestamp}')


try:
    connection = psycopg2.connect(user = setting.POSTGRES_USER,
                                password=setting.POSTGRES_PASSWORD,
                                host=setting.POSTGRES_HOST,
                                port=setting.POSTGRES_PORT,
                                database=setting.POSTGRES_DB)
    print('Подключение успешно')
except Error as e:
    print(f'Ошибка подключение: {e}')
    
