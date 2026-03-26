import os
import django
import traceback
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_booking.settings')
try:
    django.setup()
    from django.db import connection
    print("Attempting to call connection.get_database_version()...")
    version = connection.get_database_version()
    print(f"Success! Version: {version}")
except Exception as e:
    print(f"Caught exception: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)
