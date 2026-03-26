import os
import sys

# Add the project directory to sys.path
sys.path.append(r'c:\Users\23csed10\Downloads\local-service-booking-master\local-service-booking-master\backend_django')

# Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')

import django
django.setup()

from django.db import connection

def drop_all_tables():
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        for table in tables:
            print(f"Dropping {table[0]}...")
            cursor.execute(f"DROP TABLE IF EXISTS `{table[0]}`;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    print("All tables dropped.")

if __name__ == "__main__":
    drop_all_tables()
