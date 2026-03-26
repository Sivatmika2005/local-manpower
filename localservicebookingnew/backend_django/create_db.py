import pymysql
from decouple import config

host = config('DB_HOST', default='localhost')
user = config('DB_USER', default='root')
password = config('DB_PASSWORD', default='root')
db_name = config('DB_NAME', default='service_booking_new')

try:
    conn = pymysql.connect(host=host, user=user, password=password)
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully (or already exists).")
except Exception as e:
    print(f"Error: {e}")
