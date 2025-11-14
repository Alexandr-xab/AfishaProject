import pandas as pd
from sqlalchemy import create_engine 

db_config = {'user': 'praktikum_student', # имя пользователя
    'pwd': 'Sdf4$2;d-d30pp', # пароль
    'host': 'rc1b-wcoijxj3yxfsf3fs.mdb.yandexcloud.net',
    'port': 6432, # порт подключения
    'db': 'data-analyst-afisha' # название базы данных
} 
connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(
    db_config['user'],
    db_config['pwd'],
    db_config['host'],
    db_config['port'],
    db_config['db'],
) 

engine = create_engine(connection_string) 

query = '''
    SELECT
        -- Информация о пользователе:
        user_id,
        device_type_canonical,
        -- Информация о заказе:     
        order_id, -- Номер заказа
        created_dt_msk AS order_dt, -- Дата заказа
        created_ts_msk AS order_ts, -- Время заказа
        currency_code, -- Код валюты
        revenue, -- Выручка сервиса
        tickets_count, -- Кол-во билетов
        -- Время между заказами для каждого пользователя:
        created_dt_msk::date - LAG(created_dt_msk::date ) 
            OVER(PARTITION BY user_id ORDER BY created_dt_msk)
            AS days_since_prev,
        -- Информация о мероприятии:  
            p.event_id,
            service_name,
            e.event_name_code AS event_name,
            e.event_type_main,
            -- Выгрузка информации о городе и регионе:
            r.region_name,
            c.city_name
        FROM afisha.purchases AS p
        INNER JOIN afisha.events AS e USING (event_id)
        LEFT JOIN afisha.city AS c USING(city_id)
        LEFT JOIN afisha.regions AS r USING(region_id)
    WHERE
        -- Фильтрация по типу устройства
        device_type_canonical IN ('mobile','desktop') 
        -- Убираем данные о фильмах
        AND
        e.event_type_main != 'фильм'
    ORDER BY user_id;
''' 

df = pd.read_sql_query(query, con=engine) 

df.to_csv('afisha.csv', index=False)
