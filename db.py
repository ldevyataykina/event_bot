import mysql.connector
import config

from utils import get_local_time

class DataBase:
    def __init__(self, db_params, db_info):
        self.db_info = db_info
        self.db = mysql.connector.connect(host=db_params['host'],
                                          user=db_params['user'],
                                          password=db_params['password'])
        self.cursor = self.db.cursor()

        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_info['db_name']}")
        self.cursor.execute(f"ALTER DATABASE {db_info['db_name']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        self.cursor.execute(f"USE {self.db_info['db_name']}")

        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {db_info['table_name']} " \
                            f"({config.EventTableColumns.event_id} VARCHAR(255), " \
                            f"{config.EventTableColumns.event_name} VARCHAR(255), " \
                            f"{config.EventTableColumns.start_date} DATE, " \
                            f"{config.EventTableColumns.start_time} TIME, "\
                            # f"{config.EventTableColumns.end_date} DATE, " \
                            # f"{config.EventTableColumns.end_time} TIME, " \
                            # f"{config.EventTableColumns.length} INT, " \
                            f"{config.EventTableColumns.description} VARCHAR(255), "\
                            f"{config.EventTableColumns.price} VARCHAR(255), " \
                            f"{config.EventTableColumns.city} VARCHAR(255), " \
                            f"{config.EventTableColumns.address} VARCHAR(255), " \
                            f"{config.EventTableColumns.latitude} FLOAT(32), " \
                            f"{config.EventTableColumns.longitude} FLOAT(32), " \
                            f"{config.EventTableColumns.contacts} VARCHAR(255), "
                            f"{config.EventTableColumns.event_type} VARCHAR(255) )")
        self.cursor.execute(f"ALTER TABLE {db_info['table_name']} CONVERT TO CHARACTER "
                            f"SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

    def add_data(self, **d_values):
        data_to_add = d_values
        id = f'"{data_to_add["event_id"]}"'

        for key, value in data_to_add.items():
            value = f'"{value}"' if value and value != 'NULL' else value
            if key == 'event_id':
                add_query = f"INSERT INTO {self.db_info['table_name']} ({key}) " \
                            f"VALUES (%s);" % str(value)
            else:
                add_query = f"UPDATE {self.db_info['table_name']} " \
                            f"SET {key} = %s " \
                            f"WHERE event_id = {id}" % str(value)
            self.cursor.execute(add_query)
            self.db.commit()

        # columns = ', '.join(list(d_values.keys()))
        # values = ', '.join([f"'{str(value)}'" for value in d_values.values()])
        # add_query = f"INSERT INTO {self.db_info['table_name']} ({columns}) VALUES ({values});"
        # self.cursor.execute(add_query)
        # self.db.commit()

    def extract_data(self, geo):
        local_time = get_local_time(geo).strftime("%Y-%m-%d %H:%M:%S")

        extract_query = f"SELECT *, " \
                        f"(6371 * 2 * ASIN(SQRT(POWER(SIN(({geo[0]} - latitude) * pi() / 180 / 2), 2) + COS(" \
                        f"{geo[0]} * pi() / 180) * COS(latitude * pi() / 180) * POWER(" \
                        f"SIN(({geo[1]} - longitude) * pi() / 180 / 2), 2)))) as DISTANCE, " \
                        f"CONCAT(START_DATE, ' ', START_TIME) as EVENT_DATE " \
                        f"FROM {self.db_info['table_name']} " \
                        f"HAVING EVENT_DATE >= '{local_time}' " \
                        f"AND DISTANCE <= 5 " \
                        f"ORDER BY EVENT_DATE, DISTANCE " \
                        f"LIMIT 10;"

        self.cursor.execute(extract_query)
        data = self.cursor.fetchall()
        return data

    def get_id(self, city):
        query = f"SELECT DISTINCT(event_id) from {self.db_info['table_name']} " \
                f"WHERE city = '{city}'"
        self.cursor.execute(query)
        ids = self.cursor.fetchall()
        if ids:
            ids = [id[0] for id in ids]
        return ids

if __name__ == "__main__":
    import yaml
    from config import AccessInfo

    access_info = yaml.full_load(open(AccessInfo.config_file, 'r'))

    # Инициализация объекта базы данных для записи и извлечения данных
    db = DataBase(access_info['db_params'], access_info['db_info'])
    db.extract_data([55.80634, 37.60869])

